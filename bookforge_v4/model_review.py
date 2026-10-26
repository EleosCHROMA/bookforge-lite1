"""Expose fixed model findings only while their reviewed source hashes match."""
import json
from pathlib import Path


def report(packet,notes=None):
    if notes is None:
        notes=json.loads((Path(__file__).parent/'data/model_review_notes.json').read_text())
    recorded={item['id']:item for item in notes['items']}
    items=[]
    for item in packet['items']:
        found=recorded.get(item['id'])
        state='NOT_REVIEWED' if found is None else 'CURRENT_MODEL_REVIEW' if found['content_sha256']==item['content_sha256'] else 'STALE_MODEL_REVIEW'
        items.append({'id':item['id'],'state':state,'finding':found})
    return {'items':items,'total_items':len(items),
            'current_model_reviews':sum(item['state']=='CURRENT_MODEL_REVIEW' for item in items),
            'remaining_item_ids':[item['id'] for item in items if item['state']!='CURRENT_MODEL_REVIEW'],
            'human_approvals_granted':0,'note':'Fixed model-assisted findings, not human attestations or proof of complete curriculum coverage.'}
