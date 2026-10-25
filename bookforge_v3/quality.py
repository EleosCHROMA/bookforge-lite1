"""Deterministic content readiness report; not an independent pedagogy audit."""
from .math_audit import audit

REQUIRED_REVIEWS = ("mathematics", "pedagogy", "proofreading", "print_preview")

def analyze(project):
    errors, warnings = [], []
    chapters = project.get("chapters", [])
    if not isinstance(chapters, list):
        return {"ready_for_build": False, "ready_for_publication": False,
                "errors": ["chapters must be a list"], "warnings": [], "statistics": {}}
    seen, count, tickets = set(), 0, 0
    for i, ch in enumerate(chapters, 1):
        if not isinstance(ch, dict):
            errors.append(f"Chapter {i} must be an object")
            continue
        problems = ch.get("problems", [])
        if not isinstance(problems, list):
            errors.append(f"Chapter {i} problems must be a list")
            continue
        count += len(problems)
        repair = ch.get("repair_tickets", [])
        if not isinstance(repair, list):
            errors.append(f"Chapter {i} repair_tickets must be a list")
            repair = []
        tickets += len(repair)
        for p in problems:
            if not isinstance(p, dict):
                errors.append(f"Chapter {i} contains a non-object exercise")
                continue
            pid = p.get("id")
            if not isinstance(pid, str) or not pid.strip():
                errors.append(f"Chapter {i} has a missing exercise ID")
            elif pid in seen:
                errors.append(f"Duplicate exercise ID: {pid}")
            else:
                seen.add(pid)
            prompt = p.get("prompt", "")
            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(f"Blank exercise prompt: {pid}")
            elif len(prompt) > 160:
                warnings.append(f"Long prompt needs layout inspection: {pid}")
        for ticket in repair:
            if not isinstance(ticket, dict):
                errors.append(f"Chapter {i} contains a non-object ticket")
            elif len(str(ticket.get("diagnosis", ""))) > 230:
                warnings.append(f"Long repair diagnosis needs layout inspection: {ticket.get('id')}")
        answers = ch.get("answers", {})
        if isinstance(answers, dict):
            for pid, answer in answers.items():
                if not isinstance(answer, str) or not answer.strip():
                    errors.append(f"Empty answer for: {pid}")
                elif len(answer) > 250:
                    warnings.append(f"Long answer needs layout inspection: {pid}")
    checked = 0
    try:
        checked = audit(project)["checked"]
    except (ValueError, TypeError, KeyError, ArithmeticError) as exc:
        errors.append(f"Math audit failed: {exc}")
    if count > checked:
        warnings.append(f"{count - checked} exercises lack independent arithmetic checks; non-numeric questions require human review")
    from .standards_audit import report as standards_report
    standards = standards_report(project)
    if standards["invalid_or_unreviewed_standard_tags"]:
        errors.append("Invalid/unreviewed standard tags: " + ", ".join(standards["invalid_or_unreviewed_standard_tags"]))
    if standards["duplicate_prompt_pairs"]:
        warnings.append(f'{len(standards["duplicate_prompt_pairs"])} identical question prompts found')
    if standards["standards_verified_in_metadata"] < standards["standards_total"]:
        warnings.append(f'Standards mapping incomplete: {standards["standards_verified_in_metadata"]} of {standards["standards_total"]} codes have reviewed question tags')
    if standards["exercises_missing_kind"]:
        warnings.append(f'{len(standards["exercises_missing_kind"])} exercises lack an exercise-kind label')
    review = project.get("editorial_review", {})
    if not isinstance(review, dict):
        review = {}
    missing = [key for key in REQUIRED_REVIEWS if review.get(key) is not True]
    if missing:
        warnings.append("Editorial review not signed off: " + ", ".join(missing))
    return {"ready_for_build": not errors,
            "ready_for_publication": not errors and not missing,
            "errors": errors, "warnings": warnings,
            "standards_audit": standards, "statistics": {"chapters": len(chapters), "exercises": count,
                           "repair_tickets": tickets, "math_checks": checked,
                           "math_checks_remaining": max(0, count - checked),
                           "editorial_signoffs_remaining": missing}}
