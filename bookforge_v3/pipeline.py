"""BookForge v3 multi-chapter orchestration on top of the v2 renderer."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
V2_ROOT = ROOT.parent / "bookforge_v2"
THEMES = ("clean-premium", "playful-illustrated")

def validate_project(data):
    if not isinstance(data, dict):
        raise ValueError("Project must be a JSON object")
    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        raise ValueError("At least one chapter is required")
    if data.get("theme", THEMES[0]) not in THEMES:
        raise ValueError("Unknown theme")
    numbers = []
    for chapter in chapters:
        if not isinstance(chapter, dict):
            raise ValueError("Each chapter must be an object")
        numbers.append(chapter.get("chapter_number"))
        problems = chapter.get("problems")
        if not isinstance(problems, list) or not problems:
            raise ValueError("Each chapter needs exercises")
        if set(chapter.get("answers", {})) != {p.get("id") for p in problems}:
            raise ValueError("Each exercise needs exactly one keyed answer")
    if any(type(n) is not int for n in numbers) or numbers != list(range(1, len(numbers) + 1)):
        raise ValueError("Chapter numbers must start at 1 and remain sequential")
    return data

def build(project_path, output_path, theme=None):
    project = validate_project(json.loads(Path(project_path).read_text(encoding="utf-8")))
    if str(ROOT.parent) not in sys.path:
        sys.path.insert(0, str(ROOT.parent))
    from bookforge_v3.math_audit import audit
    audit(project)
    theme = theme or project.get("theme", THEMES[0])
    if theme not in THEMES:
        raise ValueError("Unknown theme")
    if not V2_ROOT.exists():
        raise FileNotFoundError("bookforge_v2 must be alongside bookforge_v3")
    if str(V2_ROOT) not in sys.path:
        sys.path.insert(0, str(V2_ROOT))
    from themes import generate
    from preflight import check_pdf
    output = generate({"chapters": project["chapters"]}, output_path, theme)
    result = check_pdf(output)
    if not result["ok"]:
        Path(output).unlink(missing_ok=True)
        raise RuntimeError("PDF preflight failed: " + "; ".join(result["issues"]))
    return {"output": str(output), "pages": result["pages"], "chapters": len(project["chapters"]), "theme": theme}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--theme", choices=THEMES)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.project, args.output, args.theme), indent=2))
