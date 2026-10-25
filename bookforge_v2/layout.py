"""Stable workbook page sizing for BookForge v2."""
from math import ceil

PROBLEMS_PER_PAGE = 6

def worksheet_batches(problems):
    """Split nonempty practice lists into two-column, three-row worksheet pages."""
    if not isinstance(problems, list) or not problems:
        raise ValueError("problems must be a nonempty list")
    return [problems[i:i + PROBLEMS_PER_PAGE] for i in range(0, len(problems), PROBLEMS_PER_PAGE)]

def section_page_count(chapter):
    """Opener + worksheet pages + repair ticket page."""
    return 2 + ceil(len(chapter["problems"]) / PROBLEMS_PER_PAGE)
