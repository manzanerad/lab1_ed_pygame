import os
import glob
from telemetry.reader import parse_line


class QualityReport:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self._reset()

    def _reset(self):
        self.files_processed = 0
        self.lines_read = 0
        self.valid_events = 0
        self.corrupt_lines = 0
        self.sessions = {}
        self.incomplete_sessions = 0

    def inspect(self):
        self._reset()
        if not os.path.isdir(self.log_dir):
            return self

        pattern = os.path.join(self.log_dir, "events_*.log")
        for path in sorted(glob.glob(pattern)):
            self.files_processed += 1
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    self.lines_read += 1
                    event = parse_line(line)
                    if event is None:
                        self.corrupt_lines += 1
                    else:
                        self.valid_events += 1
                        self._track_session(event)

        self.incomplete_sessions = sum(
            1 for ended in self.sessions.values() if not ended
        )
        return self

    def _track_session(self, event):
        sid = event["session_id"]
        et = event["event_type"]

        if et == "SESSION_START":
            if sid not in self.sessions:
                self.sessions[sid] = False
        elif et == "SESSION_END":
            self.sessions[sid] = True

    def __str__(self):
        total = self.lines_read or 1
        valid_pct = self.valid_events / total * 100
        corrupt_pct = self.corrupt_lines / total * 100
        return (
            f"Archivos procesados:     {self.files_processed}\n"
            f"Lineas leidas:           {self.lines_read}\n"
            f"Eventos validos:         {self.valid_events}  ({valid_pct:.2f}%)\n"
            f"Lineas corruptas:        {self.corrupt_lines}  ({corrupt_pct:.2f}%)\n"
            f"Sesiones incompletas:    {self.incomplete_sessions}"
        )
