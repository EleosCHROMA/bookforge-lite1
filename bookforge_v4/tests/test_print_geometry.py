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

    def test_stroke_width_is_included_in_artwork_margins(self):
        c=canvas.Canvas(str(self.path),pagesize=(612,792))
        c.drawString(42,700,'Safe text')
        c.setLineWidth(4)
        c.line(28,100,28,300)  # Center is inside the 27pt gutter; stroke extends to 26pt.
        c.showPage();c.save()
        result=audit(self.path)
        self.assertFalse(result['ok'])
        self.assertEqual(result['page_reports'][0]['violations'],0)
        self.assertEqual(result['page_reports'][0]['artwork_violations'],1)

    def test_filled_shapes_outside_margin_are_detected(self):
        c=canvas.Canvas(str(self.path),pagesize=(612,792))
        c.drawString(42,700,'Safe text')
        c.rect(20,100,30,30,stroke=0,fill=1)
        c.showPage();c.save()
        self.assertFalse(audit(self.path)['ok'])

    def test_low_resolution_image_is_rejected(self):
        from PIL import Image
        from reportlab.lib.utils import ImageReader
        c=canvas.Canvas(str(self.path),pagesize=(612,792))
        c.drawString(42,700,'Safe text')
        c.drawImage(ImageReader(Image.new('RGB',(100,100),'red')),42,500,width=144,height=144)
        c.showPage();c.save()
        result=audit(self.path)
        self.assertFalse(result['ok'])
        self.assertEqual(result['images_checked'],1)
        self.assertEqual(result['page_reports'][0]['image_details'][0]['effective_minimum_ppi'],50)

    def test_high_resolution_image_passes_without_rasterizing_vectors(self):
        from PIL import Image
        from reportlab.lib.utils import ImageReader
        c=canvas.Canvas(str(self.path),pagesize=(612,792))
        c.drawString(42,700,'Safe text')
        c.drawImage(ImageReader(Image.new('RGB',(600,600),'blue')),42,500,width=144,height=144)
        c.setLineWidth(1);c.rect(42,100,40,40)
        c.showPage();c.save()
        result=audit(self.path)
        self.assertTrue(result['ok'],result['errors'])
        self.assertEqual(result['images_checked'],1)
        self.assertEqual(result['vector_objects_checked'],1)

    def test_image_resolution_requirement_cannot_be_disabled(self):
        self.make_pdf([(42,700)])
        with self.assertRaises(ValueError):audit(self.path,minimum_image_ppi=0)
