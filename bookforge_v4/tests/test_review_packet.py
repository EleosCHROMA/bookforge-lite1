import copy
import json
import unittest
from pathlib import Path
from bookforge_v3.build_repair_draft import create as create_book
from bookforge_v4.review_packet import create,audit

ROOT=Path(__file__).resolve().parents[2]


class ReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.project=create_book(json.loads((ROOT/'bookforge_v3/data/mistake_mechanics_six_chapters.json').read_text()))
        self.lessons=json.loads((ROOT/'bookforge_v4/data/lessons.json').read_text())
        self.packet=create(self.project,self.lessons)

    def attestation(self,item,**updates):
        return {'reviewer':'Synthetic unit-test reviewer','reviewed_at':'2026-10-25T23:00:00-07:00',
                'notes':'Synthetic fixture only, not a real editorial review.',
                'content_sha256':item['content_sha256'],'decision':'approve',**updates}

    def test_all_content_types_pending_by_default(self):
        self.assertEqual(self.packet['total_items'],174)
        self.assertEqual(self.packet['counts'],{'practice':132,'repair_ticket':12,'guided_task':12,
            'lesson_concept':6,'worked_example':6,'diagram':6})
        result=audit(self.packet,{})
        self.assertEqual(result['counts']['PENDING'],174)
        self.assertFalse(result['all_items_approved'])
        first=self.packet['items'][0]
        self.assertIn('answer',first['content']['source'])

    def test_approval_matches_exact_source_only(self):
        item=self.packet['items'][0]
        reviews={item['id']:self.attestation(item)}
        self.assertEqual(audit(self.packet,reviews)['counts']['APPROVED'],1)
        pid=self.project['chapters'][0]['problems'][0]['id']
        self.project['chapters'][0]['answers'][pid]='changed answer'
        changed=create(self.project,self.lessons)
        self.assertEqual(audit(changed,reviews)['counts']['STALE'],1)

    def test_diagram_edit_invalidates_both_diagram_and_worked_review(self):
        ids=('lesson:1:diagram','lesson:1:example:1')
        reviews={item['id']:self.attestation(item) for item in self.packet['items'] if item['id'] in ids}
        self.lessons['lessons'][0]['diagram']['divisor']=[1,4]
        result=audit(create(self.project,self.lessons),reviews)
        self.assertEqual(result['counts']['STALE'],2)

    def test_missing_metadata_naive_dates_and_bad_decisions_are_invalid(self):
        item=self.packet['items'][0]
        for changes in ({'reviewer':''},{'reviewed_at':'2026-10-25T23:00:00'},
                        {'reviewed_at':'not a date'},{'reviewed_at':'2999-01-01T00:00:00Z'},{'decision':True},{'content_sha256':'bad'}):
            with self.subTest(changes=changes):
                result=audit(self.packet,{item['id']:self.attestation(item,**changes)})
                self.assertEqual(result['counts']['INVALID'],1)

    def test_rejection_and_unknown_ids_do_not_approve(self):
        item=self.packet['items'][0]
        result=audit(self.packet,{item['id']:self.attestation(item,decision='reject'), 'removed-item':{}})
        self.assertEqual(result['counts']['REJECTED'],1)
        self.assertEqual(result['unknown_review_ids'],['removed-item'])
        self.assertFalse(result['all_items_approved'])

    def test_packet_integrity_and_source_snapshot(self):
        packet=copy.deepcopy(self.packet)
        packet['items'][0]['content']['source']['answer']='tampered'
        with self.assertRaisesRegex(ValueError,'fingerprint mismatch'):audit(packet,{})
        before=copy.deepcopy(self.packet)
        self.project['chapters'][0]['problems'][0]['prompt']='changed'
        self.assertEqual(before,self.packet)
