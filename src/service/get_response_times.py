from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
from src.models import ResponseTime

INTERVALS_MAP = {
    "1min": "1T",
    "5min": "5T",
    "10min": "10T",
    "30min": "30T",
    "1h": "1H",
    "3h": "3H",
    "6h": "6H",
    "12h": "12H",
    "24h": "24H",
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
    interval: grouping interval like '1min', '5min', '1h'
    n: number of aggregated points to return
    """
    if interval not in INTERVALS_MAP:
        raise ValueError("Invalid interval")

    # Estimate how many raw records to fetch
    # Fetch last n * 2 intervals to ensure enough data for resampling
    # (adjust based on your data density)
    multiplier = RECORDS_MAP[interval]
    records = (
        db.query(ResponseTime)
        .order_by(ResponseTime.timestamp.desc())
        .limit(n * multiplier)  # fetch more to ensure enough for resampling
        .all()
    )
    
    if not records:
        return []

    # Convert to DataFrame
    df = pd.DataFrame([{
        "timestamp": r.timestamp,
        "avg_response_time": r.avg_response_time,
        "requests_count": r.requests_count
    } for r in records])

    # Sort ascending
    df.sort_values("timestamp", inplace=True)
    df.set_index("timestamp", inplace=True)

    # Resample by interval, weighted avg by requests_count
    resampled = df.resample(INTERVALS_MAP[interval]).apply(
        lambda x: (x['avg_response_time'] * x['requests_count']).sum() / max(x['requests_count'].sum(), 1)
    )

    # Take only last n points
    resampled = resampled.tail(n).reset_index().rename(columns={0: "avg_response_time"})

    result = [
        {"timestamp": ts.isoformat(), "avg_response_time": avg}
        for ts, avg in zip(resampled["timestamp"], resampled[0])
    ]
    return result
