import tempfile
import unittest
from pathlib import Path

from bookforge import build_logbook, validate_inputs


class TestBookForge(unittest.TestCase):
    def test_rejects_blank_vehicle_name(self):
        with self.assertRaises(ValueError):
            validate_inputs("   ", 10)

    def test_rejects_zero_records(self):
        with self.assertRaises(ValueError):
            validate_inputs("My Car", 0)

    def test_rejects_too_many_records(self):
        with self.assertRaises(ValueError):
            validate_inputs("My Car", 251)

    def test_builds_pdf_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "test_logbook.pdf"
            result = build_logbook(output, "Test Car", records=2)
            self.assertEqual(result, output)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 1000)
            with output.open("rb") as pdf:
                self.assertEqual(pdf.read(4), b"%PDF")

    def test_escapes_vehicle_name_in_pdf_generation(self):
        # Characters such as ampersands and angle brackets must not break PDF markup.
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "safe_name.pdf"
            build_logbook(output, "Cars & Trucks <Test>", records=1)
            self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
