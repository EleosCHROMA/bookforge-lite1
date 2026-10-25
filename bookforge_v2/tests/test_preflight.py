import tempfile
import unittest
from pathlib import Path
from reportlab.pdfgen import canvas
from preflight import check_pdf

class PreflightTests(unittest.TestCase):
    def test_rejects_non_letter_and_builtin_helvetica(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'bad.pdf'
            c=canvas.Canvas(str(path),pagesize=(600,800))
            c.setFont('Helvetica',10)
            c.drawString(30,730,'test')
            c.save()
            report=check_pdf(path)
            self.assertFalse(report['ok'])
            self.assertTrue(any('US Letter' in v for v in report['issues']))
            self.assertTrue(any('Helvetica' in v for v in report['issues']))

    def test_existing_sample_passes(self):
        from themes import generate
        import json
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'sample/chapter_full.json').read_text())
        with tempfile.TemporaryDirectory() as td:
            path=generate(data,Path(td)/'good.pdf')
            self.assertTrue(check_pdf(path)['ok'])
