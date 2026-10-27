import hashlib
import json
import tempfile
import unittest
import warnings
from pathlib import Path
from zipfile import ZipFile
from bookforge_v4.review_archive import FILES, verify


class ReviewArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.archive = self.root/'review.zip'
        self.evidence = self.root/'evidence.json'
        self.contents = {name: name.encode() for name in FILES}
        self.record = {'review_type': 'USER_REPORTED_FINAL_ONLINE_PREVIEW_PASS',
                       **{key: hashlib.sha256(self.contents[name]).hexdigest() for name, key in FILES.items()}}
        self.evidence.write_text(json.dumps(self.record))
        self.write_archive(self.contents)

    def write_archive(self, contents):
        with ZipFile(self.archive, 'w') as bundle:
            for name, data in contents.items():
                bundle.writestr(name, data)

    def test_matching_files_and_altered_file(self):
        self.assertTrue(verify(self.archive, self.evidence)['ok'])
        contents = dict(self.contents)
        contents[next(iter(FILES))] = b'changed'
        self.write_archive(contents)
        self.assertFalse(verify(self.archive, self.evidence)['ok'])

    def test_missing_and_duplicate_files_fail(self):
        contents = dict(self.contents)
        del contents[next(iter(FILES))]
        self.write_archive(contents)
        self.assertFalse(verify(self.archive, self.evidence)['ok'])
        self.write_archive(self.contents)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with ZipFile(self.archive, 'a') as bundle:
                bundle.writestr(next(iter(FILES)), b'duplicate')
        self.assertFalse(verify(self.archive, self.evidence)['ok'])

    def test_missing_or_unapproved_evidence_fails(self):
        self.record['review_type'] = 'UNKNOWN'
        self.evidence.write_text(json.dumps(self.record))
        self.assertFalse(verify(self.archive, self.evidence)['ok'])
        self.evidence.unlink()
        self.assertFalse(verify(self.archive, self.evidence)['ok'])
