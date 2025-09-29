from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
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
    if interval not in INTERVALS_MAP:
        raise ValueError("Invalid interval")

    multiplier = RECORDS_MAP[interval]
    records = (
        db.query(ResponseTime)
        .order_by(ResponseTime.timestamp.desc())
        .limit(n * multiplier)
        .all()
    )

    if not records:
        return []

    df = pd.DataFrame([{
        "timestamp": r.timestamp,
        "avg_response_time": r.avg_response_time,
        "requests_count": r.requests_count
    } for r in records])

    df.sort_values("timestamp", inplace=True)
    df.set_index("timestamp", inplace=True)

    def weighted_avg(x):
        total_count = x['requests_count'].sum()
        if total_count == 0:
            return None
        return (x['avg_response_time'] * x['requests_count']).sum() / total_count

    resampled = df.resample(INTERVALS_MAP[interval]).apply(weighted_avg)
    resampled = resampled.tail(n).reset_index().rename(columns={0: "avg_response_time"})

    result = [
        {"timestamp": ts.isoformat(), "avg_response_time": avg}
        for ts, avg in zip(resampled["timestamp"], resampled["avg_response_time"])
    ]
    return result

