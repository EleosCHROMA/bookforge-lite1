"""Build a v4 development candidate with diagrams and measured text margins."""
import argparse
import json
from pathlib import Path
from bookforge_v3.candidate import build as build_v3, write_json
from .diagrams import model, KINDS
from .print_geometry import audit as geometry_audit
from .review_packet import create as create_review_packet, audit as audit_reviews

ROOT=Path(__file__).resolve().parent


def build(output,reviews_path=None):
    reviews=json.loads(Path(reviews_path).read_text(encoding="utf-8")) if reviews_path else {}
    if not isinstance(reviews,dict):
        raise ValueError("Reviews must be an object keyed by item ID")
    lessons_path=ROOT/'data/lessons.json'
    lessons=json.loads(lessons_path.read_text(encoding='utf-8'))
    models=[{'chapter':lesson['chapter_number'],**model(lesson.get('diagram'))}
            for lesson in lessons['lessons']]
    if sorted(item['kind'] for item in models)!=sorted(KINDS):
        raise ValueError('V4 candidate requires all six visual model types')
    result=build_v3(output,lessons_path=lessons_path)
    output=Path(output).resolve()
    summary=output/'candidate-summary.json'
    # A v3 pass is insufficient: no success summary survives a failed v4 check.
    summary.unlink()
    for theme,report in result['themes'].items():
        geometry=geometry_audit(output/theme/'interior.pdf')
        write_json(output/theme/'print-geometry.json',geometry)
        if not geometry['ok']:
            raise ValueError(f'{theme}: print geometry preflight failed')
        report['text_geometry_passed']=True
        report['glyphs_checked']=geometry['glyphs_checked']
        report['artwork_geometry_passed']=True
        report['vector_objects_checked']=geometry['vector_objects_checked']
        report['images_checked']=geometry['images_checked']
    write_json(output/'diagram-models.json',{'models':models,
        'note':'Computed model parameters, not independent approval of the paired instructional text.'})
    project=json.loads((output/'manuscript.json').read_text(encoding='utf-8'))
    packet=create_review_packet(project,lessons)
    reviewed=audit_reviews(packet,reviews)
    write_json(output/'editorial-review-items.json',packet)
    write_json(output/'review-attestations.json',reviews)
    write_json(output/'review-status.json',reviewed)
    from bookforge_v3.release_manifest import sha256
    for theme in result['themes']:
        handoff_path=output/theme/'handoff.json'
        handoff=json.loads(handoff_path.read_text(encoding='utf-8'))
        for name in ('diagram-models.json','editorial-review-items.json','review-attestations.json'):
            path=output/name
            handoff['files'][name]={'sha256':sha256(path),'bytes':path.stat().st_size}
        write_json(handoff_path,handoff)
    result.update(version=4,development_status='IN_PROGRESS',visual_models=len(models),
                  editorial_items=reviewed['total_items'],editorial_status_counts=reviewed['counts'])
    write_json(summary,result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reviews',type=Path,help='Existing reviewer-supplied attestations; never generated approvals')
    args=parser.parse_args()
    print(json.dumps(build(args.output,args.reviews),indent=2))
