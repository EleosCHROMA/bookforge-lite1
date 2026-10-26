"""Model-proposed exercise metadata. Never sets reviewed standards or approvals."""
import copy


def annotate(project):
    result=copy.deepcopy(project)
    for chapter in result['chapters']:
        number=chapter['chapter_number']
        for problem in chapter['problems']:
            prompt=problem['prompt'].lower()
            kind=problem.get('kind')
            if not kind:
                kind='word_problem' if prompt.startswith(('a car','a shop','five tires','eight bolts')) else 'computation'
            if number==1:tags=['6.NS.1' if 'divided by' in prompt or 'refill' in prompt else '6.NS.3']
            elif number==2:tags=['6.RP.1' if 'ratio' in prompt or prompt.startswith('simplify') else '6.RP.3' if '%' in prompt or 'percent' in prompt or 'discount' in prompt else '6.RP.2']
            elif number==3:
                tags=['6.EE.8' if 'inequality' in prompt else '6.EE.7' if 'solve' in prompt else '6.EE.3' if 'simplify' in prompt or 'expand' in prompt else '6.EE.1' if '^' in prompt else '6.EE.2']
            elif number==4:tags=['6.NS.8' if 'distance' in prompt or 'moves' in prompt else '6.NS.6' if 'reflect' in prompt or 'quadrant' in prompt else '6.NS.7']
            elif number==5:tags=['6.G.4' if 'surface' in prompt else '6.G.2' if 'volume' in prompt else '6.G.1']
            else:tags=['6.SP.4','6.SP.5'] if 'dot plot' in prompt else ['6.SP.3']
            problem['kind']=kind
            problem.setdefault('candidate_standards',tags)
            problem['alignment_proposal']={'method':'model-assisted content inspection',
                'status':'PROPOSED_NOT_VERIFIED',
                'scope_note':'Related skill only; an isolated computation does not establish complete standard coverage.'}
    return result
