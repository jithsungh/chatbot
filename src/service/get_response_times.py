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
    Returns intervals with avg_response_time = None if no requests were recorded.
    """

    if interval not in INTERVALS_MAP:
        raise ValueError(f"Invalid interval: {interval}")

    try:
        multiplier = RECORDS_MAP.get(interval, 1)

        # Fetch latest records, ordered by timestamp descending
        records = (
            db.query(ResponseTime)
            .order_by(ResponseTime.timestamp.desc())
            .limit(n * multiplier)
            .all()
        )

        # Handle case: no records in DB
        if not records:
            logger.warning(f"No ResponseTime records found for interval '{interval}'")
            now = pd.Timestamp.now()
            last_n_index = pd.date_range(end=now, periods=n, freq=INTERVALS_MAP[interval])
            return [{"timestamp": ts.isoformat(), "avg_response_time": None} for ts in last_n_index]

        # Convert to DataFrame
        df = pd.DataFrame([{
            "timestamp": r.timestamp,
            "avg_response_time": r.avg_response_time,
            "requests_count": r.requests_count
        } for r in records])

        if df.empty:
            logger.warning("DataFrame is empty after converting records")
            now = pd.Timestamp.now()
            last_n_index = pd.date_range(end=now, periods=n, freq=INTERVALS_MAP[interval])
            return [{"timestamp": ts.isoformat(), "avg_response_time": None} for ts in last_n_index]

        # Prepare DataFrame
        df.sort_values("timestamp", inplace=True)
        df.set_index("timestamp", inplace=True)        # Weighted average function
        def weighted_avg(group):
            if group.empty:
                return None
            total_count = group['requests_count'].sum()
            if total_count == 0:
                return None
            weighted_sum = (group['avg_response_time'] * group['requests_count']).sum()
            return weighted_sum / total_count

        # Resample and compute weighted average - use agg instead of apply
        resampled = df.resample(INTERVALS_MAP[interval]).agg({
            'avg_response_time': weighted_avg
        })

        # Ensure exactly n points
        last_n_index = pd.date_range(
            end=resampled.index.max() if not resampled.empty else pd.Timestamp.now(),
            periods=n,
            freq=INTERVALS_MAP[interval]
        )
        
        # Reindex with proper handling of the Series
        resampled_series = resampled['avg_response_time'].reindex(last_n_index, fill_value=None)

        # Convert to list of dicts
        result = [
            {"timestamp": ts.isoformat(), "avg_response_time": avg}
            for ts, avg in resampled_series.items()
        ]

        return result

    except Exception as e:
        logger.error(f"Error in get_last_n_avg_response_times: {str(e)}", exc_info=True)
        raise

