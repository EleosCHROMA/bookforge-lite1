"""Independent exact-fraction validation for the fraction division bank."""
from fractions import Fraction
from .fraction_division import PAIRS, mixed

def audit_fraction_bank(project):
    expected={}
    for index,(left,right) in enumerate(PAIRS,1):
        key=f"fraction_division_{index:02d}"
        expected[key]=(f"Calculate {left} divided by {right}. Give a simplified answer.",
                       mixed(Fraction(left)/Fraction(right)))
    found={}
    for chapter in project.get("chapters",[]):
        for problem in chapter.get("problems",[]):
            key=problem.get("id")
            if key in expected:
                if key in found:
                    raise ValueError(f"Duplicate fraction question {key}")
                found[key]=(problem.get("prompt"),chapter.get("answers",{}).get(key))
    if found and set(found)!=set(expected):
        raise ValueError("Incomplete fraction-division exercise bank")
    for key,pair in found.items():
        if pair!=expected[key]:
            raise ValueError(f"Fraction exercise or answer mismatch: {key}")
    return {"checked":len(found),"total_bank_size":len(expected)}
