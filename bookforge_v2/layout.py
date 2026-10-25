"""Shared pagination rules for BookForge workbooks."""
from math import ceil

PROBLEMS_PER_PAGE = 6

def worksheet_batches(problems):
    """Split practice exercises into stable two-column, three-row pages."""
    if not isinstance(problems, list) or not problems:
        raise ValueError('problems must be a nonempty list')
    return [problems[i:i + PROBLEMS_PER_PAGE] for i in range(0, len(problems), PROBLEMS_PER_PAGE)]

def section_page_count(chapter):
    return 1 + ceil(len(chapter['problems']) / PROBLEMS_PER_PAGE) + 1
