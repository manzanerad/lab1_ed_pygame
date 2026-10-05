from typing import Iterator, Optional, Dict
import os
import glob
import time
import re


LOG_DIR = "logs"
ROTATION_BYTES = 512 * 1024


class LogWriter:
    def __init__(self, log_dir: str = LOG_DIR, buffer_size: int = 10):
        self.log_dir = log_dir
        self.buffer_size = buffer_size
        self.buffer = []
        self.session_id = f"S{int(time.time() * 1000) % 1000000:06d}"
        os.makedirs(log_dir, exist_ok=True)
        self.current_file = self._next_filename()
        self.handle = open(self.current_file, "a", encoding="utf-8")

    def _next_filename(self):
        pattern = os.path.join(self.log_dir, "events_*.log")
        files = glob.glob(pattern)
        max_num = 0
        for f in files:
            m = re.match(r"events_(\d+)\.log$", os.path.basename(f))
            if m:
                max_num = max(max_num, int(m.group(1)))
        return os.path.join(self.log_dir, f"events_{max_num + 1:03d}.log")

    def _rotate(self):
        self.flush(force=True)
        self.handle.close()
        self.current_file = self._next_filename()
        self.handle = open(self.current_file, "a", encoding="utf-8")

    def log(self, event_type: str, params: Dict[str, object]):
        parts = [f"{k}={v}" for k, v in params.items()]
        line = f"{time.time():.3f}|{self.session_id}|{event_type}|{';'.join(parts)}\n"
        self.buffer.append(line)
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self, force: bool = False):
        if not self.buffer:
            return
        self.handle.writelines(self.buffer)
        self.handle.flush()
        self.buffer.clear()
        if os.path.getsize(self.current_file) >= ROTATION_BYTES:
            self._rotate()

    def close(self):
        self.flush(force=True)
        if self.handle:
            self.handle.close()
            self.handle = None


def parse_line(line: str) -> Optional[Dict[str, object]]:
    line = line.strip()
    if not line:
        return None
    fields = line.split("|")
    if len(fields) != 4:
        return None
    ts, session, ev_type, payload = fields
    try:
        timestamp = float(ts)
    except ValueError:
        return None
    params: Dict[str, str] = {}
    for item in payload.split(";"):
        if not item or "=" not in item:
            return None
        key, value = item.split("=", 1)
        if not key:
            return None
        params[key] = value
    return {
        "timestamp": timestamp,
        "session": session,
        "type": ev_type,
        "params": params,
    }


def iter_events(log_dir: str = LOG_DIR) -> Iterator[Dict[str, object]]:
    if not os.path.exists(log_dir):
        return
    pattern = os.path.join(log_dir, "events_*.log")
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                event = parse_line(line)
                if event is not None:
                    yield event


def data_quality_report(log_dir: str = LOG_DIR) -> Dict[str, object]:
    total = 0
    valid = 0
    corrupt = 0
    starts = set()
    ends = set()

    if not os.path.exists(log_dir):
        return {
            "files": 0,
            "lines": 0,
            "valid": 0,
            "valid_pct": 0.0,
            "corrupt": 0,
            "corrupt_pct": 0.0,
            "incomplete": 0,
        }

    pattern = os.path.join(log_dir, "events_*.log")
    files = sorted(glob.glob(pattern))

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                total += 1
                event = parse_line(line)
                if event is None:
                    corrupt += 1
                else:
                    valid += 1
                    if event["type"] == "SESSION_START":
                        starts.add(str(event["session"]))
                    elif event["type"] == "SESSION_END":
                        ends.add(str(event["session"]))

    incomplete = len(starts - ends)
    valid_pct = (valid / total * 100) if total else 0.0
    corrupt_pct = (corrupt / total * 100) if total else 0.0

    return {
        "files": len(files),
        "lines": total,
        "valid": valid,
        "valid_pct": valid_pct,
        "corrupt": corrupt,
        "corrupt_pct": corrupt_pct,
        "incomplete": incomplete,
    }
