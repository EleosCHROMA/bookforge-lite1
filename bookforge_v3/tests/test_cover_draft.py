import json
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.cover_draft import geometry, draft

class CoverDraftTests(unittest.TestCase):
    def test_sixty_page_premium_color_dimensions(self):
        config=geometry(60)
        self.assertAlmostEqual(config["spine_in"],.14082)
        self.assertAlmostEqual(config["width_in"],17.39082)
        self.assertAlmostEqual(config["height_in"],11.25)
        self.assertFalse(config["spine_text_allowed"])
    def test_eighty_page_spine_text_eligibility(self):
        self.assertTrue(geometry(80)["spine_text_allowed"])
        with self.assertRaises(ValueError):geometry(20)
        with self.assertRaises(ValueError):geometry(829)
    def test_both_themes_embedded_fonts(self):
        with tempfile.TemporaryDirectory() as t:
            for theme in ("clean-premium","playful-illustrated"):
                path=Path(t)/(theme+".pdf")
                settings=draft(path,theme=theme)
                page=PdfReader(str(path)).pages[0]
                self.assertAlmostEqual(float(page.mediabox.width)/72,settings["width_in"],places=3)
                self.assertEqual(len(PdfReader(str(path)).pages),1)
                for ref in page["/Resources"]["/Font"].get_object().values():
                    descriptor=ref.get_object().get("/FontDescriptor")
                    self.assertIsNotNone(descriptor)
                    self.assertTrue(any(key in descriptor.get_object() for key in
                                        ("/FontFile","/FontFile2","/FontFile3")))
    def test_unknown_ink_rejected(self):
        with self.assertRaises(ValueError):geometry(60,paper="unknown")
