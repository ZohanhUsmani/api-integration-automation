"""Lightweight cron-like scheduler."""
import time
import threading


class Scheduler:
    def __init__(self):
        self.jobs = []
        self._stop = threading.Event()

    def every(self, seconds, func, *a, **k):
        def loop():
            while not self._stop.is_set():
                func(*a, **k)
                self._stop.wait(seconds)
        t = threading.Thread(target=loop, daemon=True)
        self.jobs.append(t)
        t.start()
        return t

    def stop(self):
        self._stop.set()