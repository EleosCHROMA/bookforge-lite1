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
from bookforge_v3.release_manifest import sha256


def audit(root, preview=None):
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
        if load('editorial-review-items.json') != packet:
            result['blockers'].append('Saved editorial packet differs from current manuscript and lessons')
        from .model_review import report as model_review_report
        result['model_assisted_review']=model_review_report(packet)
        if load('model-editorial-review.json') != result['model_assisted_review']:
            result['blockers'].append('Saved model review differs from current source-bound findings')
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
        result['preview_status']='NOT_RECORDED'
        if preview is not None:
            evidence=json.loads(Path(preview).read_text(encoding='utf-8'))
            theme=evidence.get('theme')
            if theme not in ('clean-premium','playful-illustrated'):
                raise ValueError('Invalid preview theme')
            hashes_match=(evidence.get('interior_sha256')==sha256(root/theme/'interior.pdf') and
                          evidence.get('cover_sha256')==sha256(root/theme/'cover.pdf'))
            if hashes_match and evidence.get('review_type')=='USER_REPORTED_FINAL_ONLINE_PREVIEW_PASS':
                result['preview_status']='USER_REPORTED_PASS_FOR_MATCHING_PACKAGE'
                result['preview_note']='User-reported pass; uploaded bytes are not independently authenticated.'
            else:
                result['preview_status']='STALE_OR_INVALID'
        if result['preview_status']!='USER_REPORTED_PASS_FOR_MATCHING_PACKAGE':
            result['blockers'].append('KDP Previewer review is needed for the final file set')
        result['blockers'].append('Explicit user publication approval is required')
        result['print_proof_note']='User elected to skip physical proof if the online preview looks good; no physical proof is recorded.'
    except (OSError,ValueError,TypeError,KeyError) as exc:
        result['engineering_ready']=False
        result['blockers'].append('Readiness audit failed: '+str(exc))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--preview',type=Path,help='User-reported final online preview evidence')
    args=parser.parse_args()
    report=audit(args.directory,args.preview)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('themes','editorial_review','integrity')},indent=2))
    raise SystemExit(0 if report['engineering_ready'] else 1)
