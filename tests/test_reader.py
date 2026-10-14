import unittest
from telemetry.reader import parse_line, iter_events
import os
import tempfile


class TestReader(unittest.TestCase):
    def test_valid_line(self):
        line = "1717000012.412|S0007|SESSION_START|player=ana;difficulty=normal\n"
        e = parse_line(line)
        self.assertEqual(e["timestamp"], 1717000012.412)
        self.assertEqual(e["session_id"], "S0007")
        self.assertEqual(e["event_type"], "SESSION_START")
        self.assertEqual(e["params"]["player"], "ana")

    def test_empty_line(self):
        self.assertIsNone(parse_line(""))
        self.assertIsNone(parse_line("   \n"))
        self.assertIsNone(parse_line("\n"))

    def test_wrong_field_count(self):
        self.assertIsNone(parse_line("a|b|c\n"))
        self.assertIsNone(parse_line("a|b|c|d|e\n"))

    def test_bad_timestamp(self):
        self.assertIsNone(parse_line("abc|S0007|EVENT|x=1\n"))

    def test_missing_equals(self):
        e = parse_line("1717000012.412|S0007|EVENT|x=1;malformado;y=2\n")
        self.assertEqual(e["params"]["x"], "1")
        self.assertEqual(e["params"]["y"], "2")
        self.assertNotIn("malformado", e["params"])

    def test_iter_events_streaming(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "events_001.log")
            with open(path, "w", encoding="utf-8") as f:
                f.write("1.0|S1|SESSION_START|player=ana\n")
                f.write("2.0|S1|SESSION_END|score=100;level=1;duration=1.0;result=quit\n")

            events = list(iter_events(tmp))
            self.assertEqual(len(events), 2)


if __name__ == "__main__":
    unittest.main()
