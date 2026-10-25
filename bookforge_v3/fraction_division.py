"""Exact Grade 6 fraction-division problem generator (draft lesson content)."""
from fractions import Fraction

PAIRS = [
 ("3/4","1/2"),("2/3","1/6"),("5/8","1/4"),("3/5","2/5"),
 ("7/9","7/18"),("4/5","2/3"),("5/6","1/3"),("9/10","3/5"),
 ("2/7","4/7"),("7/8","1/2"),("3/4","2/3"),("5/12","5/6"),
]

def mixed(value):
    value = Fraction(value)
    whole, rem = divmod(value.numerator, value.denominator)
    if rem == 0:
        return str(whole)
    if whole:
        return f"{whole} {rem}/{value.denominator}"
    return f"{rem}/{value.denominator}"

def make_exercises():
    questions = []
    for n,(left,right) in enumerate(PAIRS,1):
        result = Fraction(left) / Fraction(right)
        questions.append({
            "id": f"fraction_division_{n:02d}",
            "prompt": f"Calculate {left} divided by {right}. Give a simplified answer.",
            "kind": "computation",
            "answer": mixed(result),
            "exact_numerator": result.numerator,
            "exact_denominator": result.denominator,
            "candidate_standards": ["6.NS.1"],
            "standard_reviewed": False,
        })
    return questions
