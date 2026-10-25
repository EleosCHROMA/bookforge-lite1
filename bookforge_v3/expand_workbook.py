"""Expand six-chapter draft with 72 deterministic, arithmetic-checked problems.
This is a QA fixture, not independently reviewed instructional material.
"""
import argparse
import json
from pathlib import Path
from .math_audit import evaluate

ADDITIONS = {
1:[('Calculate 8.6 + 3.45','8.6+3.45',''),('Calculate 18.4 - 9.75','18.4-9.75',''),('Calculate 0.24 x 1.5','0.24*1.5',''),('Calculate 7.5 / 0.5','7.5/0.5',''),('Calculate 6.08 + 0.97','6.08+0.97',''),('Calculate 14 - 2.86','14-2.86',''),('Calculate 3.2 x 0.25','3.2*0.25',''),('Calculate 12.6 / 0.3','12.6/0.3',''),('Calculate 0.875 + 1.125','0.875+1.125',''),('Calculate 30 - 8.45','30-8.45',''),('Calculate 4.5 x 1.2','4.5*1.2',''),('Calculate 0.96 / 0.08','0.96/0.08','')],
2:[('Find 25% of 84','84*.25',''),('Find 15% of 200','200*.15',''),('Find 60% of 35','35*.6',''),('A car drives 210 miles in 3 hours. Find miles per hour.','210/3',' mph'),('A shop charges $288 for 4 hours. Find dollars per hour.','288/4',' dollars/hour'),('Five tires cost $425. Find the cost of one tire.','425/5',' dollars'),('Find 30% of 90','90*.3',''),('A car drives 156 miles using 6 gallons. Find mpg.','156/6',' mpg'),('Find 12% of 150','150*.12',''),('Eight bolts cost $32. Find dollars per bolt.','32/8',' dollars'),('A car drives 360 miles in 6 hours. Find mph.','360/6',' mph'),('Find 75% of 48','48*.75','')],
3:[('Evaluate 7 x 4 + 3','7*4+3',''),('Evaluate 2 x (8 + 5)','2*(8+5)',''),('Evaluate 40 - 6 x 5','40-6*5',''),('Evaluate (18 + 6) / 3','(18+6)/3',''),('Evaluate 9 x 3 - 4','9*3-4',''),('Solve x + 13 = 39. Find x.','39-13',''),('Solve 7x = 63. Find x.','63/7',''),('Solve y - 19 = 8. Find y.','8+19',''),('Evaluate 6 x (5 - 2)','6*(5-2)',''),('Evaluate 4 x 4 + 9','4*4+9',''),('Solve z / 6 = 8. Find z.','8*6',''),('Evaluate 100 - 8 x 7','100-8*7','')],
4:[('Find | -17 |','17',''),('Find | -9 | + | 4 |','9+4',''),('Find vertical distance from y=-4 to y=7','7-(-4)',' units'),('Find horizontal distance from x=-6 to x=3','3-(-6)',' units'),('Find | -12 | - | -5 |','12-5',''),('Find | -8 | + | -7 |','8+7',''),('Find distance between (-3,2) and (-3,9)','9-2',' units'),('Find distance between (4,-5) and (4,1)','1-(-5)',' units'),('Find | -21 |','21',''),('Find | -15 | + 2','15+2',''),('Find distance from x=-2 to x=10','10-(-2)',' units'),('Find | -19 | - | 6 |','19-6','')],
5:[('Area of rectangle 6 cm x 8 cm','6*8',' sq cm'),('Triangle area: base 10 m and height 8 m','10*8/2',' sq m'),('Volume of box 3 x 4 x 5 cm','3*4*5',' cubic cm'),('Area of parallelogram: base 12 and height 7','12*7',' sq units'),('Surface area of cube with side 3 cm','6*3*3',' sq cm'),('Trapezoid area: bases 4 and 8, height 5','(4+8)*5/2',' sq units'),('Volume of box 2.5 x 4 x 3 cm','2.5*4*3',' cubic cm'),('Area of triangle: base 9 and height 6','9*6/2',' sq units'),('Area of rectangle 7.5 m x 2 m','7.5*2',' sq m'),('Surface area of cube with side 5 cm','6*5*5',' sq cm'),('Volume of box 6 x 2 x 4 in','6*2*4',' cubic in'),('Area of trapezoid: bases 7 and 13, height 4','(7+13)*4/2',' sq units')],
6:[('Mean of 6, 12, 18','(6+12+18)/3',''),('Range of 8, 16, 27, 11','27-8',''),('Mean of 5, 7, 9, 11','(5+7+9+11)/4',''),('IQR if Q1=9 and Q3=24','24-9',''),('Mean of 10, 20, 40, 30','(10+20+40+30)/4',''),('Range of 31, 14, 22, 9','31-9',''),('Mean of 3, 6, 9, 12, 15','(3+6+9+12+15)/5',''),('IQR if Q1=11 and Q3=33','33-11',''),('Range of 88, 12, 45, 61','88-12',''),('Mean of 2, 4, 8, 10','(2+4+8+10)/4',''),('IQR if Q1=7 and Q3=19','19-7',''),('Mean of 15, 25, 35, 45','(15+25+35+45)/4','')]
}

def expand(project):
    project=json.loads(json.dumps(project))
    if len(project['chapters'])!=6:
        raise ValueError('Expansion expects six chapters')
    checks=project.setdefault('math_checks',[])
    for chapter in project['chapters']:
        number=chapter['chapter_number']
        for position,(prompt,expression,suffix) in enumerate(ADDITIONS[number],7):
            pid=f'c{number}p{position}'
            value=evaluate(expression)
            answer=f'{value.normalize():f}{suffix}'
            chapter['problems'].append({'id':pid,'prompt':prompt,'provenance':'deterministic-original-draft'})
            chapter['answers'][pid]=answer
            checks.append({'problem_id':pid,'expression':expression,'expected':str(value),'answer_text':answer})
    project['source_note']='Expanded engineering-only draft: 36 reference-adapted plus 72 deterministic original questions; not editorially approved.'
    project['editorial_review']={}
    return project

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    project=expand(json.loads(args.input.read_text(encoding='utf-8')))
    args.output.write_text(json.dumps(project,indent=2)+'\n',encoding='utf-8')
