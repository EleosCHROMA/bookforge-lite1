"""Re-run engineering checks on saved artifacts without granting publication approval."""
import argparse
import json
from pathlib import Path
from .verify_package import verify
from .print_geometry import audit as geometry_audit
from .review_packet import create, audit as review_audit
from bookforge_v3.manuscript_audit import audit as manuscript_audit
from bookforge_v3.paired_cover_preflight import paired_preflight
from bookforge_v3.quality import analyze


def audit(root):
    root=Path(root).resolve()
    integrity=verify(root)
    result={'engineering_ready':False,'ready_for_publication':False,
            'integrity':integrity,'themes':{},'blockers':[]}
    if not integrity['ok']:
        result['blockers']=integrity['errors']
        return result
    try:
        load=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
        project,lessons=load('manuscript.json'),load('lessons.json')
        quality=analyze(project)
        result['content_checks']=quality
        if not quality['ready_for_build']:
            result['blockers'].extend(quality['errors'])
        packet=create(project,lessons)
        from .model_review import report as model_review_report
        result['model_assisted_review']=model_review_report(packet)
        reviews=review_audit(packet,load('review-attestations.json'))
        result['editorial_review']=reviews
        for theme in ('clean-premium','playful-illustrated'):
            interior,cover=root/theme/'interior.pdf',root/theme/'cover.pdf'
            config=load(f'{theme}/cover-config.json')
            checks={'manuscript':manuscript_audit(interior,project,
                [lesson['title'] for lesson in lessons['lessons']],lessons),
                'print_geometry':geometry_audit(interior),
                'paired_cover':paired_preflight(interior,cover,config['paper_stock'])}
            result['themes'][theme]={key:{k:v for k,v in report.items() if k!='page_reports'}
                                     for key,report in checks.items()}
            for key,report in checks.items():
                if not report['ok']:result['blockers'].append(f'{theme}: {key} failed')
        result['engineering_ready']=not result['blockers']
        if not reviews['all_items_approved']:
            pending=reviews['total_items']-reviews['counts']['APPROVED']
            result['blockers'].append(f'{pending} content items lack current valid editorial approvals')
        result['blockers'].extend(['KDP Previewer and print proof require actual review',
                                  'Explicit user publication approval is required'])
    except (OSError,ValueError,TypeError,KeyError) as exc:
        result['engineering_ready']=False
        result['blockers'].append('Readiness audit failed: '+str(exc))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=audit(args.directory)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('themes','editorial_review','integrity')},indent=2))
    raise SystemExit(0 if report['engineering_ready'] else 1)
