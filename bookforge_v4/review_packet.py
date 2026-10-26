"""Content-bound editorial worklist. Generating a packet never approves it."""
import hashlib
import json
import re
from datetime import datetime, timezone


def fingerprint(content):
    encoded=json.dumps(content,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def create(project,lessons):
    items=[]
    seen=set()

    def add(key,kind,chapter,source):
        if key in seen:raise ValueError('Duplicate editorial item ID: '+key)
        seen.add(key)
        content={'kind':kind,'chapter':chapter,'source':source}
        # Snapshot source objects so callers cannot invalidate a generated packet by mutation.
        content=json.loads(json.dumps(content))
        items.append({'id':key,'content_sha256':fingerprint(content),'content':content})

    for chapter in project['chapters']:
        number=chapter['chapter_number']
        for index,problem in enumerate(chapter['problems'],1):
            add('practice:'+problem['id'],'practice',number,
                {'chapter_title':chapter['chapter_title'],'number':index,
                 'problem':problem,'answer':chapter['answers'][problem['id']]})
        for ticket in chapter['repair_tickets']:
            add(f"repair:{number}:{ticket['id']}",'repair_ticket',number,ticket)
    for lesson in lessons['lessons']:
        number=lesson['chapter_number']
        context={'title':lesson['title'],'concept':lesson['concept']}
        add(f'lesson:{number}:concept','lesson_concept',number,context)
        for index,example in enumerate(lesson['examples'],1):
            add(f'lesson:{number}:example:{index}','worked_example',number,
                {**context,'example':example,'diagram':lesson.get('diagram')})
        if len(lesson['guided'])!=len(lesson['guided_answers']):
            raise ValueError('Guided prompt/solution count mismatch')
        for index,(prompt,answer) in enumerate(zip(lesson['guided'],lesson['guided_answers']),1):
            add(f'lesson:{number}:guided:{index}','guided_task',number,
                {**context,'prompt':prompt,'answer':answer})
        if 'diagram' in lesson:
            add(f'lesson:{number}:diagram','diagram',number,
                {**context,'diagram':lesson['diagram'],'paired_examples':lesson['examples']})
    counts={kind:sum(item['content']['kind']==kind for item in items)
            for kind in sorted({item['content']['kind'] for item in items})}
    return {'schema_version':1,'items':items,'counts':counts,'total_items':len(items),
            'note':'Reviewer worklist includes solutions. Do not insert it into student pages. No editorial approvals are generated.'}


def audit(packet,reviews):
    if not isinstance(reviews,dict):raise ValueError('Reviews must be an object keyed by item ID')
    statuses=[]
    seen=set()
    for item in packet['items']:
        key=item['id']
        if key in seen:raise ValueError('Duplicate item in review packet')
        seen.add(key)
        current=fingerprint(item['content'])
        if current!=item['content_sha256']:
            raise ValueError('Review packet content fingerprint mismatch: '+key)
        entry=reviews.get(key)
        status,reason='PENDING','No review supplied'
        if key in reviews:
            status,reason='INVALID','Incomplete review metadata'
            if isinstance(entry,dict):
                valid=all(isinstance(entry.get(field),str) and entry[field].strip()
                          for field in ('reviewer','reviewed_at','notes','content_sha256'))
                valid=valid and entry.get('decision') in ('approve','reject')
                valid=valid and re.fullmatch(r'[0-9a-f]{64}',entry.get('content_sha256','')) is not None
                if valid:
                    try:
                        reviewed_at=datetime.fromisoformat(entry['reviewed_at'].replace('Z','+00:00'))
                        valid=(reviewed_at.utcoffset() is not None
                               and reviewed_at <= datetime.now(timezone.utc))
                    except ValueError:valid=False
                if valid:
                    if entry['content_sha256']!=current:
                        status,reason='STALE','Source changed since review'
                    elif entry['decision']=='reject':
                        status,reason='REJECTED','Reviewer rejected this source version'
                    else:
                        status,reason='APPROVED','Supplied attestation matches this source version'
        statuses.append({'id':key,'status':status,'reason':reason})
    unknown=sorted(set(reviews)-seen)
    counts={status:sum(item['status']==status for item in statuses)
            for status in ('PENDING','INVALID','STALE','REJECTED','APPROVED')}
    return {'total_items':len(statuses),'counts':counts,'unknown_review_ids':unknown,
            'all_items_approved':bool(statuses) and counts['APPROVED']==len(statuses) and not unknown,
            'items':statuses,
            'warning':'Attestations are supplied metadata. Reviewer identity and expertise are not authenticated. This audit does not authorize publication.'}


if __name__=='__main__':
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser()
    parser.add_argument('--project',required=True,type=Path)
    parser.add_argument('--lessons',required=True,type=Path)
    parser.add_argument('--reviews',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    load=lambda path:json.loads(path.read_text(encoding='utf-8'))
    packet=create(load(args.project),load(args.lessons))
    report=audit(packet,load(args.reviews))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key!='items'},indent=2))
    raise SystemExit(0 if report['all_items_approved'] else 1)
