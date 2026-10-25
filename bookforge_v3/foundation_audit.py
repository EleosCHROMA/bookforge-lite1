"""Independent checks for 15 original non-decimal answer types.

Recomputes expected results from fixed problem definitions and rejects changed
question prompts. This is engineering verification, NOT editorial sign-off.
"""
from fractions import Fraction
from statistics import median
from math import gcd

def _ratio(a,b):
    g=gcd(a,b)
    return f"{a//g}:{b//g}"

def _linear_value(a,b,total):
    return (total-b)/a

CASES = {
    "c2p1": ("Simplify the ratio 8:12",lambda:_ratio(8,12)),
    "c2p2": ("120 dollars for 3 hours; hourly rate?",lambda:f"${Fraction(120,3)} per hour"),
    "c2p3": ("240 miles in 4 hours; distance in 7 hours?",lambda:f"{Fraction(240,4)*7} miles"),
    "c2p5": ("Simplify 18:24",lambda:_ratio(18,24)),
    "c3p2": ("Simplify 7m + 4 - 2m + 5",lambda:f"{7-2}m + {4+5}"),
    "c3p3": ("Expand 6(2r + 5)",lambda:f"{6*2}r + {6*5}"),
    "c3p4": ("Solve p - 14 = 28",lambda:f"p = {_linear_value(1,-14,28):g}"),
    "c3p5": ("Solve 8w = 96",lambda:f"w = {_linear_value(8,0,96):g}"),
    "c4p2": ("Compare -8 and -3",lambda:"-8 < -3" if -8 < -3 else "-8 > -3"),
    "c4p3": ("Distance between (5,-2) and (5,6)",lambda:f"{abs(6-(-2))} units"),
    "c4p4": ("Reflect (2,-4) across x-axis",lambda:f"({2},{-(-4)})"),
    "c4p5": ("Quadrant of (-6,-3)",lambda:"Quadrant III" if -6<0 and -3<0 else "Unknown"),
    "c4p6": ("Reflect (-3,7) across y-axis",lambda:f"({-(-3)},{7})"),
    "c6p1": ("Median: 12, 18, 11, 15, 20, 14",lambda:str(median([12,18,11,15,20,14]))),
    "c6p3": ("Median: 3, 9, 2, 7, 11, 5",lambda:str(median([3,9,2,7,11,5]))),
}

def verify(project):
    found={}
    for chapter in project.get("chapters",[]):
        answers=chapter.get("answers",{})
        for item in chapter.get("problems",[]):
            key=item.get("id")
            if key in CASES:
                if key in found:raise ValueError(f"Duplicate foundation ID: {key}")
                found[key]=(item.get("prompt"),answers.get(key))
    if not found:
        return {"checked":0,"bank_size":len(CASES)}
    if set(found)!=set(CASES):
        raise ValueError("Incomplete foundation question bank")
    for key,(expected_prompt,compute) in CASES.items():
        prompt,answer=found[key]
        if prompt!=expected_prompt:
            raise ValueError(f"Original prompt changed: {key}")
        expected=compute()
        if answer!=expected:
            raise ValueError(f"Independent answer mismatch for {key}: expected {expected!r}")
    return {"checked":len(found),"bank_size":len(CASES)}
