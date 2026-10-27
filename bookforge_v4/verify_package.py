"""Verify exact candidate file bytes without approving publication."""
import argparse
import json
from pathlib import Path
from bookforge_v3.release_manifest import sha256


def verify(root):
    root=Path(root).resolve()
    errors=[]
    checked=0
    for theme in ('clean-premium','playful-illustrated'):
        path=root/theme/'handoff.json'
        try:
            report=json.loads(path.read_text(encoding='utf-8'))
            files=report['files']
            if not isinstance(files,dict) or not files:
                raise ValueError('Empty or invalid file inventory')
            for required in ('manuscript.json','lessons.json',f'{theme}/interior.pdf',f'{theme}/cover.pdf',
                             'editorial-review-items.json','review-attestations.json','editorial-review.html',
                             'diagram-models.json','model-editorial-review.json'):
                if required not in files:errors.append(f'{theme}: missing inventory entry {required}')
            for name,record in files.items():
                target=(root/name).resolve()
                if not target.is_relative_to(root):
                    errors.append(f'{theme}: path escapes package: {name}')
                    continue
                if not target.is_file():
                    errors.append(f'{theme}: missing file: {name}')
                elif target.stat().st_size!=record['bytes'] or sha256(target)!=record['sha256']:
                    errors.append(f'{theme}: changed file: {name}')
                else:checked+=1
        except (OSError,ValueError,KeyError,TypeError) as exc:
            errors.append(f'{theme}: invalid handoff: {exc}')
    return {'ok':not errors,'fingerprints_checked':checked,'errors':errors,
            'ready_for_publication':False,
            'warning':'Byte integrity only. Handoffs are not signed; this does not authenticate reviewers or authorize publication.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    args=parser.parse_args()
    report=verify(args.directory)
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report['ok'] else 1)
