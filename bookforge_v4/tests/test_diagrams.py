import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from pypdf import PdfReader
from bookforge_v3.lesson_pages import render, validate_lessons
from bookforge_v4.diagrams import model

ROOT = Path(__file__).resolve().parents[1]


class DiagramTests(unittest.TestCase):
    def setUp(self):
        self.lessons=json.loads((ROOT/'data/lessons.json').read_text())

    def test_computed_worked_results(self):
        models=[model(l['diagram']) for l in self.lessons['lessons']]
        self.assertEqual(Fraction(models[0]['quotient']), Fraction(3,2))
        self.assertEqual(models[1]['unit_rate'], '9')
        self.assertEqual(models[1]['target_cost'], '45')
        self.assertTrue(models[2]['included'])
        self.assertTrue(models[2]['left'])
        self.assertEqual(models[3]['reflected'], (2,-2))
        self.assertEqual(models[4]['surface_area'],52)
        self.assertEqual(models[4]['volume'],24)
        self.assertEqual(models[5]['mean'],'17')
        self.assertEqual(models[5]['median'],15)
        self.assertEqual(Fraction(models[5]['mad']),Fraction(22,5))
        self.assertEqual(sum(models[5]['frequencies'].values()),5)

    def test_fraction_grid_uses_common_denominator(self):
        result=model({'kind':'fraction_groups','dividend':[2,3],'divisor':[1,6]})
        self.assertEqual(result['denominator'],6)
        self.assertEqual(result['numerator'],4)
        self.assertEqual(result['group_cells'],1)
        self.assertEqual(result['quotient'],'4')

    def test_strict_and_inclusive_inequalities(self):
        for operator,included,left in (('<',False,True),('<=',True,True),('>',False,False),('>=',True,False)):
            result=model({'kind':'inequality','operator':operator,'boundary':2000})
            self.assertEqual((result['included'],result['left']),(included,left))

    def test_invalid_math_and_unreadable_data_rejected(self):
        invalid=[{'kind':'unknown'},
            {'kind':'fraction_groups','dividend':[3,0],'divisor':[1,2]},
            {'kind':'unit_rate','quantity':0,'total':27,'target':5},
            {'kind':'inequality','boundary':True,'operator':'<='},
            {'kind':'coordinates','start':[-3,2],'shift_x':20,'reflect':'x'},
            {'kind':'prism_net','dimensions':[4,-3,2]},
            {'kind':'dot_plot','values':[1,1,1,1,2]},
            {'kind':'dot_plot','values':[1,2,4]}]
        for spec in invalid:
            with self.subTest(spec=spec),self.assertRaises(ValueError): model(spec)

    def test_six_diagram_lessons_render_with_embedded_fonts(self):
        for theme in ('clean-premium','playful-illustrated'):
            with tempfile.TemporaryDirectory() as tmp:
                output=Path(tmp)/'lessons.pdf'
                render(self.lessons,output,theme)
                pdf=PdfReader(output)
                self.assertEqual(len(pdf.pages),6)
                expected=('Shaded amount: 3/4','$9 per filter','Boundary included',
                          'Each grid step is 1 unit.','Surface area: 52 square inches','Mean: 17')
                for page,label in zip(pdf.pages,expected):
                    self.assertIn(label,page.extract_text())
                    self.assertNotIn('/XObject',page['/Resources'])
                    for font in page['/Resources']['/Font'].get_object().values():
                        self.assertIn('/FontDescriptor',font.get_object())

    def test_diagram_does_not_silently_cover_long_worked_text(self):
        lesson=copy.deepcopy(self.lessons['lessons'][0])
        lesson['examples'][0]['steps']=['A long explanation that must not overlap the visual model. '*4]*3
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):render({'lessons':[lesson]},Path(tmp)/'bad.pdf')

    def test_diagram_with_two_examples_rejected(self):
        lesson=copy.deepcopy(self.lessons['lessons'][0])
        lesson['examples']*=2
        with self.assertRaisesRegex(ValueError,'exactly one'):
            validate_lessons({'lessons':[lesson]})

    def test_number_line_spacing_and_prism_net_face_areas(self):
        import pdfplumber
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'lessons.pdf'
            render(self.lessons,output)
            with pdfplumber.open(output) as pdf:
                words=pdf.pages[2].extract_words()
                tick_top=max(w['top'] for w in words if w['text']=='0')
                ticks=[next(w for w in words if w['text']==value and abs(w['top']-tick_top)<1)
                       for value in ('0','1000','2000','3000')]
                gaps=[b['x0']-a['x0'] for a,b in zip(ticks,ticks[1:])]
                self.assertAlmostEqual(gaps[0],gaps[1],places=3)
                self.assertAlmostEqual(gaps[1],gaps[2],places=3)
                faces=[r for r in pdf.pages[4].rects if r['width']<100 and r['height']<100]
                self.assertEqual(len(faces),6)
                self.assertAlmostEqual(sum(r['width']*r['height'] for r in faces),52*49)
                for a in faces:
                    for b in faces:
                        if a is b:continue
                        overlap_width=min(a['x1'],b['x1'])-max(a['x0'],b['x0'])
                        overlap_height=min(a['bottom'],b['bottom'])-max(a['top'],b['top'])
                        self.assertFalse(overlap_width>0.01 and overlap_height>0.01)

    def test_model_tasks_have_larger_writing_space(self):
        import pdfplumber
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'lessons.pdf'
            render(self.lessons,output)
            with pdfplumber.open(output) as pdf:
                for page in pdf.pages:
                    boxes=[curve for curve in page.curves if abs(curve['width']-518)<.1]
                    self.assertEqual(sorted(round(box['height']) for box in boxes),[48,72])
                    self.assertTrue(all(box['bottom']<=738 for box in boxes))

    def test_invalid_and_oversized_workspace_requests_fail(self):
        for heights in ([True,48],[47,48],[72], [121,48]):
            lesson=copy.deepcopy(self.lessons['lessons'][0])
            lesson['guided_workspace_heights']=heights
            with self.subTest(heights=heights),self.assertRaises(ValueError):
                validate_lessons({'lessons':[lesson]})
        lesson=copy.deepcopy(self.lessons['lessons'][0])
        lesson['guided_workspace_heights']=[120,120]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'safe area'):
                render({'lessons':[lesson]},Path(tmp)/'overflow.pdf')

    def test_weight_model_includes_zero_and_rejects_unsupported_domain(self):
        spec={'kind':'inequality','boundary':2000,'operator':'<=','nonnegative':True}
        self.assertTrue(model(spec)['nonnegative'])
        spec['operator']='>'
        with self.assertRaises(ValueError):model(spec)
