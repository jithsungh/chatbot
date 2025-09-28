import threading
import time
from typing import List

from src.models import ResponseTime
from src.config import Config

class AvgResponseTimeCalculator:
    def __init__(self, interval: int = 60):
        """
        db_post_function: a callable that takes average response time and posts it to the DB
        interval: time in seconds to calculate average (default: 60 seconds)
        """
        self.response_times: List[float] = []
        self.lock = threading.Lock()
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True  # ensures thread stops when main program exits
        self._thread.start()

    def store_response_time(self, response_time: float):
        """Thread-safe function to append a response time to the list."""
        with self.lock:
            self.response_times.append(response_time)

    def _calculate_average_and_post(self):
        """Lock the list, calculate average, clear list, and post to DB."""
        with self.lock:
            if not self.response_times:
                return  # nothing to do
            times_copy = self.response_times.copy()
            self.response_times.clear()

        count = len(times_copy)
        avg_response_time = sum(times_copy) / count if count > 0 else None
        # Post to database
        session = Config.get_session()
        new_record = ResponseTime(
            average_response_time=avg_response_time,
            count=count
        )
        session.add(new_record)
        session.commit()
        session.close()

    def _run(self):
        """Background thread to run every interval seconds."""
        while not self._stop_event.is_set():
            time.sleep(self.interval)
            self._calculate_average_and_post()

    def stop(self):
        """Stop the background thread gracefully."""
        self._stop_event.set()
        self._thread.join()
