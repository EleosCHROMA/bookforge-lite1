"""Check a delivered review ZIP against recorded file fingerprints.

This verifies package bytes, not what was uploaded to KDP or who reviewed it.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import BadZipFile, ZipFile

FILES = {
    'Mistake_Mechanics_V4_Interior.pdf': 'interior_sha256',
    'Mistake_Mechanics_V4_Cover.pdf': 'cover_sha256',
}
MAX_FILE_SIZE = 100 * 1024 * 1024


def verify(archive, evidence):
    result = {'ok': False, 'files': {}, 'errors': [],
              'warning': 'Byte comparison only; KDP uploads and review identity are not authenticated.'}
    try:
        record = json.loads(Path(evidence).read_text(encoding='utf-8'))
        if record.get('review_type') != 'USER_REPORTED_FINAL_ONLINE_PREVIEW_PASS':
            raise ValueError('Evidence does not record a user-reported final online preview')
        with ZipFile(archive) as bundle:
            entries = bundle.infolist()
            for filename, key in FILES.items():
                expected = record.get(key, '')
                if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
                    raise ValueError(f'Invalid expected fingerprint: {key}')
                matches = [entry for entry in entries if entry.filename == filename]
                if len(matches) != 1:
                    result['errors'].append(f'{filename}: expected exactly one archive entry')
                    continue
                entry = matches[0]
                if entry.is_dir() or entry.file_size > MAX_FILE_SIZE:
                    result['errors'].append(f'{filename}: invalid or oversized file')
                    continue
                digest = hashlib.sha256()
                with bundle.open(entry) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(chunk)
                actual = digest.hexdigest()
                result['files'][filename] = {'bytes': entry.file_size, 'sha256': actual}
                if actual != expected:
                    result['errors'].append(f'{filename}: fingerprint differs from review evidence')
        result['ok'] = not result['errors']
    except (OSError, ValueError, TypeError, AttributeError, KeyError, RuntimeError, BadZipFile) as exc:
        result['errors'].append(f'Archive verification failed: {exc}')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.archive, args.evidence)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['ok'] else 1)
