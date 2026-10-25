"""Space-aware pagination for workbook answer-key pages."""
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics

MAX_ANSWERS_PER_PAGE = 9
ANSWER_WIDTH = 612 - 2 * 42 - 65
ROW_BUDGET = 380

def answer_row_height(answer):
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Answers must be nonempty text")
    if "BFRegular" not in pdfmetrics.getRegisteredFontNames():
        raise RuntimeError("Register BookForge fonts before measuring answers")
    lines = simpleSplit(answer, "BFRegular", 9, ANSWER_WIDTH)
    return max(33, 15 * len(lines) + 18) + 4

def answer_batches(chapter):
    """Yield batches as (first_problem_index, questions), respecting available page height."""
    problems = chapter["problems"]
    answers = chapter["answers"]
    if not problems:
        raise ValueError("Chapter requires at least one problem")
    batches, start, current, height = [], 0, [], 0
    for index, problem in enumerate(problems):
        required = answer_row_height(answers[problem["id"]])
        if required > ROW_BUDGET:
            raise ValueError(f"Answer is too long for one page: {problem['id']}")
        if current and (len(current) >= MAX_ANSWERS_PER_PAGE or height + required > ROW_BUDGET):
            batches.append((start, current))
            start, current, height = index, [], 0
        current.append(problem)
        height += required
    if current:
        batches.append((start, current))
    return batches
