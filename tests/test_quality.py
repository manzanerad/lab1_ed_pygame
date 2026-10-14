import unittest
import os
import tempfile
from telemetry.quality import QualityReport


class TestQuality(unittest.TestCase):
    def test_complete_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events_001.log")
            with open(path, "w", encoding="utf-8") as f:
                f.write("1.0|S1|SESSION_START|player=ana\n")
                f.write("2.0|S1|SESSION_END|score=100;level=1;duration=1.0;result=quit\n")

            r = QualityReport(tmp).inspect()
            self.assertEqual(r.files_processed, 1)
            self.assertEqual(r.lines_read, 2)
            self.assertEqual(r.valid_events, 2)
            self.assertEqual(r.corrupt_lines, 0)
            self.assertEqual(r.incomplete_sessions, 0)

    def test_incomplete_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events_001.log")
            with open(path, "w", encoding="utf-8") as f:
                f.write("1.0|S1|SESSION_START|player=ana\n")
                f.write("corrupta\n")

            r = QualityReport(tmp).inspect()
            self.assertEqual(r.incomplete_sessions, 1)
            self.assertEqual(r.corrupt_lines, 1)


if __name__ == "__main__":
    unittest.main()
