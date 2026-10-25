import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from reportlab.pdfgen import canvas
from pypdf import PdfReader
from bookforge_v3.cover_pipeline import make_cover, geometry, artwork_dimensions
from bookforge_v3.paired_cover_preflight import paired_preflight

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'data/cover_config.json'

class CoverPipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.dir=Path(self.tmp.name)
        self.interior=self.dir/'interior.pdf'
        c=canvas.Canvas(str(self.interior),pagesize=(612,792))
        for i in range(60):
            c.drawString(50,700,str(i+1))
            c.showPage()
        c.save()
        self.meta=json.loads(CONFIG.read_text(encoding='utf-8'))
    def tearDown(self):
        self.tmp.cleanup()
    def test_actual_page_count(self):
        cover=self.dir/'cover.pdf'
        result=make_cover(self.interior,self.meta,cover)
        self.assertEqual(result['pages'],60)
        self.assertAlmostEqual(result['spine_in'],0.14082)
        self.assertAlmostEqual(result['cover_width_in'],17.39082)
        self.assertTrue(paired_preflight(self.interior,cover)['ok'])
    def test_wrong_page_count_rejected(self):
        self.meta['expected_pages']=61
        with self.assertRaises(ValueError):
            make_cover(self.interior,self.meta,self.dir/'cover.pdf')
    def test_low_resolution_art_rejected(self):
        path=self.dir/'tiny.png'
        Image.new('RGB',(100,100),'red').save(path)
        self.assertFalse(artwork_dimensions(path,3.05,3.15)['meets_300_ppi'])
        with self.assertRaises(ValueError):
            make_cover(self.interior,self.meta,self.dir/'cover.pdf',path)
    def test_high_resolution_art_accepted(self):
        path=self.dir/'large.png'
        Image.new('RGB',(1400,1500),'red').save(path)
        result=make_cover(self.interior,self.meta,self.dir/'cover.pdf',path)
        self.assertTrue(result['artwork']['meets_300_ppi'])
        self.assertEqual(len(PdfReader(str(self.dir/'cover.pdf')).pages),1)
    def test_embedded_fonts_and_size(self):
        cover=self.dir/'cover.pdf'
        make_cover(self.interior,self.meta,cover)
        page=PdfReader(str(cover)).pages[0]
        self.assertAlmostEqual(float(page.mediabox.width)/72,17.39082,places=5)
        for font in page['/Resources']['/Font'].get_object().values():
            descriptor=font.get_object().get('/FontDescriptor')
            self.assertIsNotNone(descriptor)
            self.assertTrue(any(k in descriptor.get_object()
                for k in ('/FontFile','/FontFile2','/FontFile3')))
    def test_wrong_stock_pair_fails(self):
        cover=self.dir/'cover.pdf'
        make_cover(self.interior,self.meta,cover)
        self.assertFalse(paired_preflight(self.interior,cover,'bw-white')['ok'])
    def test_80_page_text_threshold(self):
        self.assertFalse(geometry(79)['spine_text_allowed'])
        self.assertTrue(geometry(80)['spine_text_allowed'])
