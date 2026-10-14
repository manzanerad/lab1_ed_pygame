import os
import glob


def iter_events(log_dir="logs"):
    if not os.path.exists(log_dir):
        return
    files = sorted(glob.glob(os.path.join(log_dir, "events_*.log")))
    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                event = parse_line(line)
                if event is not None:
                    yield event


def parse_line(line):
    line = line.strip()
    if not line:
        return None
    parts = line.split("|")
    if len(parts) != 4:
        return None
    timestamp, session_id, event_type, param_str = parts
    params = {}
    if param_str:
        for pair in param_str.split(";"):
            if "=" not in pair:
                continue
            k, v = pair.split("=", 1)
            params[k] = v
    return {
        "timestamp": timestamp,
        "session_id": session_id,
        "event_type": event_type,
        "params": params,
    }

