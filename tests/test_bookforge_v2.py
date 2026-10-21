"""Tests for the modular BookForge V2 foundation."""

import tempfile
import unittest
from pathlib import Path

from bookforge_v2.models import BookConfig
from bookforge_v2.renderer import render_book
from bookforge_v2.templates import VehicleMaintenanceTemplate


class BookConfigTests(unittest.TestCase):
    def test_rejects_blank_title(self):
        with self.assertRaises(ValueError):
            BookConfig(title="   ")

    def test_rejects_zero_pages(self):
        with self.assertRaises(ValueError):
            BookConfig(title="Logbook", page_count=0)


class VehicleTemplateTests(unittest.TestCase):
    def test_builds_requested_number_of_pages(self):
        pages = VehicleMaintenanceTemplate().build_pages(3)
        self.assertEqual(len(pages), 3)
        self.assertEqual(pages[0].columns[0], "Date")
        self.assertEqual(len(pages[0].rows), 12)

    def test_rejects_zero_pages(self):
        with self.assertRaises(ValueError):
            VehicleMaintenanceTemplate().build_pages(0)


class PdfRendererTests(unittest.TestCase):
    def test_creates_pdf(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "test.pdf"
            result = render_book(BookConfig(title="Test Logbook", page_count=1), VehicleMaintenanceTemplate(), output)
            self.assertEqual(result, output)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 500)
            self.assertEqual(output.read_bytes()[:5], b"%PDF-")


if __name__ == "__main__":
    unittest.main()
