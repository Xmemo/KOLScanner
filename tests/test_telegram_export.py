from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from signal_qa.telegram_export import extract_token_address, parse_export_file


class TelegramExportTests(unittest.TestCase):
    def test_extract_token_address(self) -> None:
        text = "New call\n💊CA： 9xQeWvG816bUx9EPfA8tXXkG4Y4tB5Lz9sJ7Lx8o3kQ"
        token = extract_token_address(text)
        self.assertEqual(token, "9xQeWvG816bUx9EPfA8tXXkG4Y4tB5Lz9sJ7Lx8o3kQ")

    def test_parse_sample_export(self) -> None:
        sample = Path("examples/sample_telegram_export.json")
        signals = parse_export_file(sample, channel_name="sample_channel")
        self.assertEqual(len(signals), 2)
        self.assertEqual(signals[0].channel_name, "sample_channel")
        self.assertTrue(signals[0].token_address)


if __name__ == "__main__":
    unittest.main()
