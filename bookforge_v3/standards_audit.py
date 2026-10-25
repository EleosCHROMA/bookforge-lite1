"""Conservative Grade 6 standards and exercise-mix audit.

Candidate tags are editor-authored metadata, NOT verified standards alignment.
Unknown/unreviewed problems do not count as covered.
Reference: https://www.thecorestandards.org/Math/Content/6/
"""
from collections import Counter

STANDARDS = {
    "6.RP.1": "Ratio concepts", "6.RP.2": "Unit rates", "6.RP.3": "Ratio and percent problem solving",
    "6.NS.1": "Divide fractions by fractions", "6.NS.2": "Long division",
    "6.NS.3": "Decimal operations", "6.NS.4": "GCF, LCM and distributive factoring",
    "6.NS.5": "Positive and negative quantities", "6.NS.6": "Rational-number positions",
    "6.NS.7": "Order and absolute value", "6.NS.8": "Coordinate-plane problems",
    "6.EE.1": "Exponents", "6.EE.2": "Write and evaluate expressions",
    "6.EE.3": "Equivalent expressions", "6.EE.4": "Equivalent expressions and identities",
    "6.EE.5": "Equation/inequality solution meaning", "6.EE.6": "Use variables",
    "6.EE.7": "Solve equations", "6.EE.8": "Inequalities",
    "6.EE.9": "Dependent and independent variables",
    "6.G.1": "Area of shapes", "6.G.2": "Volume with fractional edges",
    "6.G.3": "Coordinate geometry of polygons", "6.G.4": "Surface area using nets",
    "6.SP.1": "Statistical questions", "6.SP.2": "Distributions",
    "6.SP.3": "Measures of center and variability",
    "6.SP.4": "Dot plots, histograms, box plots",
    "6.SP.5": "Interpret statistics in context",
}
ALLOWED_KINDS = {"computation", "word_problem", "error_analysis", "explanation", "visual", "modeling"}
# Chapter-level editorial possibilities. Never counted as earned coverage.
CHAPTER_CANDIDATES = {
    1: ("6.NS.3",),
    2: ("6.RP.1", "6.RP.2", "6.RP.3"),
    3: ("6.EE.1", "6.EE.2", "6.EE.3", "6.EE.6", "6.EE.7"),
    4: ("6.NS.5", "6.NS.6", "6.NS.7", "6.NS.8"),
    5: ("6.G.1", "6.G.2", "6.G.4"),
    6: ("6.SP.1", "6.SP.2", "6.SP.3", "6.SP.4", "6.SP.5"),
}

def report(project):
    """Report only editor-verified per-question standard tags as coverage."""
    claimed = Counter()
    kinds = Counter()
    unknown_kinds, invalid_tags, missing_tags = [], [], []
    duplicates = []
    seen_prompts = {}
    for chapter in project.get("chapters", []):
        for p in chapter.get("problems", []):
            pid = p.get("id", "?")
            prompt = " ".join(str(p.get("prompt", "")).lower().split())
            if prompt in seen_prompts:
                duplicates.append((seen_prompts[prompt], pid))
            else:
                seen_prompts[prompt] = pid
            kind = p.get("kind")
            if kind in ALLOWED_KINDS:
                kinds[kind] += 1
            else:
                unknown_kinds.append(pid)
            tags = p.get("verified_standards", [])
            if not isinstance(tags, list):
                invalid_tags.append(pid)
                continue
            if not tags:
                missing_tags.append(pid)
            for tag in tags:
                if tag not in STANDARDS or not p.get("standard_reviewed") is True:
                    invalid_tags.append(pid)
                else:
                    claimed[tag] += 1
    covered = sorted(claimed)
    return {
        "standards_total": len(STANDARDS),
        "standards_verified_in_metadata": len(covered),
        "standards_with_verified_exercises": covered,
        "standards_without_verified_exercises": sorted(set(STANDARDS) - set(covered)),
        "chapter_candidate_standards": {str(k):list(v) for k,v in CHAPTER_CANDIDATES.items()},
        "exercise_kind_counts": dict(sorted(kinds.items())),
        "exercises_missing_kind": unknown_kinds,
        "exercises_without_verified_standard": missing_tags,
        "invalid_or_unreviewed_standard_tags": sorted(set(invalid_tags)),
        "duplicate_prompt_pairs": duplicates,
        "note": "0 verified tags means not yet reviewed, not necessarily absent from the exercises. Candidate tags are not a curriculum audit.",
    }
