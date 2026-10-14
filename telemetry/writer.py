import os
import time
import glob


class EventLogWriter:
    def __init__(self, log_dir="logs", buffer_size=10, max_size_bytes=512 * 1024):
        self.log_dir = log_dir
        self.buffer_size = buffer_size
        self.max_size_bytes = max_size_bytes
        self.session_id = self._generate_session_id()
        self._buffer = []
        self._current_file = None
        self._current_path = None
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        os.makedirs(self.log_dir, exist_ok=True)

    def _generate_session_id(self):
        return f"S{int(time.time() * 1000) % 1000000:06d}"

    def _next_file_path(self):
        existing = sorted(glob.glob(os.path.join(self.log_dir, "events_*.log")))
        n = 1
        if existing:
            last = existing[-1]
            num = int(os.path.basename(last).replace("events_", "").replace(".log", ""))
            n = num + 1
        return os.path.join(self.log_dir, f"events_{n:03d}.log")

    def _open_current(self):
        candidates = sorted(glob.glob(os.path.join(self.log_dir, "events_*.log")))
        path = candidates[-1] if candidates else self._next_file_path()
        self._current_path = path
        self._current_file = open(path, "a", encoding="utf-8")

    def _rotate_if_needed(self):
        if self._current_path is None or not os.path.exists(self._current_path):
            return
        if os.path.getsize(self._current_path) >= self.max_size_bytes:
            self._flush_buffer()
            self._current_file.close()
            self._current_path = self._next_file_path()
            self._current_file = open(self._current_path, "a", encoding="utf-8")

    def log(self, event_type, params):
        if self._current_file is None:
            self._open_current()
        timestamp = f"{time.time():.3f}"
        param_str = ";".join(f"{k}={v}" for k, v in params.items())
        line = f"{timestamp}|{self.session_id}|{event_type}|{param_str}\n"
        self._buffer.append(line)
        if len(self._buffer) >= self.buffer_size:
            self._flush_buffer()
        self._rotate_if_needed()

    def _flush_buffer(self):
        if self._buffer and self._current_file:
            self._current_file.writelines(self._buffer)
            self._current_file.flush()
            self._buffer.clear()

    def close(self):
        self._flush_buffer()
        if self._current_file:
            self._current_file.close()
            self._current_file = None











