import threading
import time
from typing import List

from src.models import ResponseTime
from src.config import Config


class AvgResponseTimeCalculator:
    def __init__(self, interval: int = 60):
        """
        interval: time in seconds to calculate average (default: 60 seconds)
        """
        self.response_times: List[float] = []
        self.lock = threading.Lock()
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
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

        session = Config.get_session()
        try:
            new_record = ResponseTime(
                avg_response_time=avg_response_time,
                requests_count=count
            )
            session.add(new_record)
            session.commit()
        finally:
            session.close()

    def _run(self):
        """Background thread that runs at the start of each minute."""
        # Align first run to the top of the next minute
        while not self._stop_event.is_set():
            now = time.time()
            # seconds until the next full minute
            sleep_time = self.interval - (now % self.interval)
            if sleep_time <= 0:
                sleep_time = self.interval
            if self._stop_event.wait(timeout=sleep_time):
                break  # stop event triggered
            self._calculate_average_and_post()

    def stop(self):
        """Stop the background thread gracefully."""
        self._stop_event.set()
        self._thread.join()
