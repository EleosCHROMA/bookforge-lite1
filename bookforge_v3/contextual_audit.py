"""Independent deterministic checks for the twelve contextual draft exercises.

Expected results are recomputed from fixed scenario inputs rather than read from
the authored answer string. This verifies key results and protects prompt/solution
integrity, not the quality of explanations or full standards alignment.
"""
from fractions import Fraction
from decimal import Decimal

def _expected():
    price_per_filter = Fraction(27, 3)
    discount = Decimal("80") * Decimal("0.25")
    values = [10, 15, 15, 20, 25]
    times = {2: 1, 3: 3, 4: 2}
    return {
        "context_1_01": str(Fraction(3,4)/Fraction(1,8)),
        "context_1_02": str(Fraction(2,3)/Fraction(1,3)),
        "context_2_01": "$"+str(price_per_filter*7),
        "context_2_02": "$"+str((Decimal("80")-discount).normalize()),
        "context_3_01": f"18h; ${18*4} when h = 4",
        "context_3_02": "w <= 2000; yes",
        "context_4_01": f"({-3+5}, 2)",
        "context_4_02": f"{min(-6,-2)} degrees",
        "context_5_01": f"{(Decimal('2.5')*Decimal('1.5')*Decimal('2')).normalize()} cubic feet",
        "context_5_02": f"{Fraction(10*6,2)} square inches",
        "context_6_01": f"{Fraction(sum(values),len(values))} minutes",
        "context_6_02": str(max(times,key=times.get)),
    }

def verify(project):
    """Validate all-or-none bank, exact source prompts, and calculated answer prefixes."""
    from .contextual_enrichment import CONTEXTUAL
    expected = _expected()
    authored = {}
    for chapter in project.get("chapters", []):
        for p in chapter.get("problems", []):
            pid = p.get("id")
            if isinstance(pid,str) and pid.startswith("context_"):
                if pid in authored:
                    raise ValueError(f"Duplicate contextual exercise: {pid}")
                authored[pid] = (chapter.get("chapter_number"),p,chapter.get("answers",{}).get(pid))
    if not authored:
        return {"checked":0,"bank_size":len(expected)}
    if set(authored) != set(expected):
        raise ValueError("Incomplete or unexpected contextual question bank")
    counters = {}
    for chapter_number,kind,prompt,_,steps,standard in CONTEXTUAL:
        counters[chapter_number]=counters.get(chapter_number,0)+1
        pid=f"context_{chapter_number}_{counters[chapter_number]:02d}"
        chapter,p,answer = authored[pid]
        if chapter!=chapter_number or p.get("prompt")!=prompt or p.get("kind")!=kind:
            raise ValueError(f"Contextual problem altered: {pid}")
        if p.get("candidate_standards")!=[standard]:
            raise ValueError(f"Contextual standard candidate altered: {pid}")
        # The expected prefix is derived independently; preserve current authored
        # explanation text as a tamper check, not as an independent proof.
        prefix=expected[pid]
        if not isinstance(answer,str) or not answer.startswith(prefix+". "):
            raise ValueError(f"Contextual computed answer mismatch: {pid}")
        if answer!=prefix+". "+steps:
            raise ValueError(f"Contextual worked explanation changed: {pid}")
    return {"checked":len(authored),"bank_size":len(expected)}
