from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from signal_qa.models import SignalMessage
from signal_qa.scoring import evaluate_signal, score_channel


class FakeMarketClient:
    def get_price_at_timestamp(self, token_address: str, timestamp: int):
        return {"price": 1.0, "timestamp": timestamp}

    def get_price_history_range(self, token_address: str, time_from: int, time_to: int):
        return {"price": {"highest": {"price": 1.5, "time": time_from + 3600}}}


class ScoringTests(unittest.TestCase):
    def test_evaluate_signal(self) -> None:
        signal = SignalMessage(
            source_file="sample.json",
            channel_name="sample_channel",
            message_id="1",
            timestamp=1000,
            signal_time_iso="1970-01-01T00:16:40+00:00",
            token_address="9xQeWvG816bUx9EPfA8tXXkG4Y4tB5Lz9sJ7Lx8o3kQ",
            raw_text="CA",
            raw_message={},
        )
        evaluation = evaluate_signal(signal, FakeMarketClient(), lookahead_hours=24)
        self.assertEqual(evaluation.status, "win")
        self.assertAlmostEqual(evaluation.return_multiple, 1.5)

    def test_score_channel(self) -> None:
        signal = SignalMessage(
            source_file="sample.json",
            channel_name="sample_channel",
            message_id="1",
            timestamp=1000,
            signal_time_iso="1970-01-01T00:16:40+00:00",
            token_address="9xQeWvG816bUx9EPfA8tXXkG4Y4tB5Lz9sJ7Lx8o3kQ",
            raw_text="CA",
            raw_message={},
        )
        evaluation = evaluate_signal(signal, FakeMarketClient(), lookahead_hours=24)
        summary = score_channel("sample_channel", ["sample.json"], 3, [evaluation])
        self.assertGreater(summary.quality_score, 0)
        self.assertNotEqual(summary.grade, "N/A")


if __name__ == "__main__":
    unittest.main()
