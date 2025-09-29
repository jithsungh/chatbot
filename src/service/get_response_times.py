import pandas as pd
from sqlalchemy.orm import Session
from fastapi.logger import logger
from src.models import ResponseTime

INTERVALS_MAP = {
    "1min": "1min",
    "5min": "5min",
    "10min": "10min",
    "30min": "30min",
    "1h": "1h",
    "3h": "3h",
    "6h": "6h",
    "12h": "12h",
    "24h": "24h",
}

RECORDS_MAP = {
    "1min": 1,
    "5min": 5,
    "10min": 10,
    "30min": 30,
    "1h": 60,
    "3h": 180,
    "6h": 360,
    "12h": 720,
    "24h": 1440,
}


def get_last_n_avg_response_times(db: Session, interval: str, n: int = 50):
    """
    Fetch last n aggregated average response times.
    Returns intervals with avg_response_time = 0 and requests_count = 0 if no requests were recorded.
    """
    if interval not in INTERVALS_MAP:
        raise ValueError(f"Invalid interval: {interval}")

    try:
        multiplier = RECORDS_MAP.get(interval, 1)
        now = pd.Timestamp.now()

        # Fetch latest records
        records = (
            db.query(ResponseTime)
            .order_by(ResponseTime.timestamp.desc())
            .limit(n * multiplier)
            .all()
        )

        if not records:
            logger.warning(f"No ResponseTime records found for interval '{interval}'")
            last_n_index = pd.date_range(end=now, periods=n, freq=INTERVALS_MAP[interval])
            return [
                {"timestamp": ts.isoformat(), "avg_response_time": 0, "requests_count": 0} 
                for ts in last_n_index
            ]

        # Convert to DataFrame
        df = pd.DataFrame([{
            "timestamp": r.timestamp,
            "avg_response_time": r.avg_response_time,
            "requests_count": r.requests_count
        } for r in records])

        if df.empty:
            last_n_index = pd.date_range(end=now, periods=n, freq=INTERVALS_MAP[interval])
            return [
                {"timestamp": ts.isoformat(), "avg_response_time": 0, "requests_count": 0} 
                for ts in last_n_index
            ]

        # Prepare DataFrame
        df.sort_values("timestamp", inplace=True)
        df.set_index("timestamp", inplace=True)

        # Resample to get sum of requests and weighted avg
        def weighted_avg(group):
            total_count = group['requests_count'].sum()
            if total_count == 0:
                return 0
            weighted_sum = (group['avg_response_time'] * group['requests_count']).sum()
            return weighted_sum / total_count

        resampled_avg = df.resample(INTERVALS_MAP[interval]).apply(weighted_avg)
        resampled_count = df['requests_count'].resample(INTERVALS_MAP[interval]).sum()

        # Ensure exactly n points
        last_n_index = pd.date_range(
            end=resampled_avg.index.max() if not resampled_avg.empty else now,
            periods=n,
            freq=INTERVALS_MAP[interval]
        )

        resampled_avg = resampled_avg.reindex(last_n_index, fill_value=0)
        resampled_count = resampled_count.reindex(last_n_index, fill_value=0)

        # Convert to list of dicts
        result = [
            {
                "timestamp": ts.isoformat(),
                "avg_response_time": float(avg),
                "requests_count": int(count)
            }
            for ts, avg, count in zip(resampled_avg.index, resampled_avg.values, resampled_count.values)
        ]

        return result

    except Exception as e:
        logger.error(f"Error in get_last_n_avg_response_times: {str(e)}", exc_info=True)
        raise
