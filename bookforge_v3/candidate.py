"""Build a complete, auditable v3 engineering candidate. Never publishes."""
import argparse
import json
from pathlib import Path
from .pipeline import ROOT, THEMES
from .build_repair_draft import create
from .native_book import assemble
from .manuscript_audit import audit
from .ticket_inventory import inventory
from .cover_pipeline import make_cover
from .release_manifest import manifest, sha256
from .release_gate import evaluate
from .review_queue import review_queue


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def build(output, lessons_path=None):
    """Refuse existing destinations; write summary only after structural success."""
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Candidate destination already exists; choose a new directory')
    lessons_path = Path(lessons_path or ROOT/'data/production_lessons.json')
    lessons = json.loads(lessons_path.read_text(encoding='utf-8'))
    project = create(json.loads((ROOT/'data/mistake_mechanics_six_chapters.json').read_text(encoding='utf-8')))
    chapters = [chapter['chapter_number'] for chapter in project['chapters']]
    if sorted(lesson.get('chapter_number', -1) for lesson in lessons['lessons']) != sorted(chapters):
        raise ValueError('Candidate requires exactly one guided lesson for every chapter')
    output.mkdir(parents=True)
    project_path = output/'manuscript.json'
    write_json(project_path, project)
    write_json(output/'lessons.json', lessons)
    tickets = inventory(project, expected_per_chapter=2)
    write_json(output/'ticket-inventory.json', tickets)
    if not tickets['ok']:
        raise ValueError('Repair ticket inventory failed')
    write_json(output/'editorial-review-queue.json', review_queue(project))
    results = {}
    for theme in THEMES:
        folder = output/theme
        folder.mkdir()
        interior, cover = folder/'interior.pdf', folder/'cover.pdf'
        built = assemble(project_path, output/'lessons.json', interior, theme)
        checked = audit(interior, project, [l['title'] for l in lessons['lessons']], lessons)
        write_json(folder/'manuscript-audit.json', checked)
        if not checked['ok']:
            raise ValueError(f'{theme}: manuscript audit failed')
        config = json.loads((ROOT/'data/cover_config.json').read_text(encoding='utf-8'))
        config.update(theme=theme, expected_pages=built['pages'])
        config['back_blurb'] = config['back_blurb'].replace('visual lessons', 'worked lessons')
        config_path = folder/'cover-config.json'
        write_json(config_path, config)
        cover_report = make_cover(interior, config, cover)
        write_json(folder/'cover-report.json', cover_report)
        handoff = manifest(project_path, interior, cover, cover_config=config_path)
        # Bind the exact guided source to the handoff as well as the manuscript.
        lesson_file = output/'lessons.json'
        handoff['files'][str(lesson_file)] = {'sha256': sha256(lesson_file), 'bytes': lesson_file.stat().st_size}
        handoff['files'] = {str(Path(path).relative_to(output)): value
                            for path, value in handoff['files'].items()}
        handoff['file_base'] = '..'
        write_json(folder/'handoff.json', handoff)
        if not handoff['ready_for_structural_review']:
            raise ValueError(f'{theme}: paired preflight failed')
        gate = evaluate(project, interior, cover_path=cover)
        write_json(folder/'release-blockers.json', gate)
        results[theme] = {'pages': built['pages'], 'answer_key_page': built['answer_key_page'],
                          'guided_lessons': built['lessons'],
                          'guided_solutions_checked': checked['guided_solutions_checked'],
                          'structural_checks_passed': True, 'publication_blockers': gate['blockers']}
    summary = {'version': 3, 'engineering_checks_passed': True,
               'ready_for_publication': False, 'themes': results,
               'note': 'Requires visual review, independent editorial approval, and KDP Previewer. Never uploads or publishes.'}
    write_json(output/'candidate-summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))
