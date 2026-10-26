import tempfile
import unittest
from pathlib import Path
from reportlab.pdfgen import canvas
from bookforge_v4.print_geometry import audit


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/'test.pdf'

    def tearDown(self):self.temp.cleanup()

    def make_pdf(self, positions):
        c=canvas.Canvas(str(self.path),pagesize=(612,792))
        for x,y in positions:
            c.setFont('Helvetica',10);c.drawString(x,y,'X');c.showPage()
        c.save()

    def test_safe_glyphs_pass(self):
        self.make_pdf([(42,700),(42,700)])
        self.assertTrue(audit(self.path)['ok'])

    def test_inside_margin_alternates_with_page_parity(self):
        self.make_pdf([(20,700),(20,700)])
        result=audit(self.path)
        self.assertFalse(result['ok'])
        self.assertEqual([p['violations'] for p in result['page_reports']],[1,0])
        self.make_pdf([(585,700),(585,700)])
        result=audit(self.path)
        self.assertEqual([p['violations'] for p in result['page_reports']],[0,1])

    def test_bottom_and_top_overflow_detected(self):
        for y in (8,785):
            self.make_pdf([(42,y)])
            self.assertFalse(audit(self.path)['ok'])

    def test_gutter_grows_with_manuscript_length(self):
        self.make_pdf([(30,700)]*151)
        result=audit(self.path)
        self.assertEqual(result['required_inside_pt'],36)
        self.assertGreater(result['page_reports'][0]['violations'],0)

    def test_margin_cannot_be_disabled(self):
        self.make_pdf([(42,700)])
        with self.assertRaises(ValueError):audit(self.path,outside_pt=0)
