# BookForge V2 — Modular Architecture Prototype

This is the first V2 development step, added on the `version-2` branch. The existing BookForge Lite implementation on `main` has not been changed.

## What is new

- `bookforge_v2/models.py` defines shared configuration and validates basic inputs.
- `bookforge_v2/templates.py` defines a small template interface and vehicle-maintenance content template.
- `bookforge_v2/renderer.py` renders template content to PDF independently of the specific book type.
- `bookforge_v2/cli.py` provides a separate V2 command-line entry point.
- `tests/test_bookforge_v2.py` covers configuration validation, template behavior, and PDF output.

This is an additive prototype: it does not replace the original CLI or delete any existing files. It is the beginning of a reusable architecture, not yet a complete multi-template product system.

## Run it on Windows

From the repository root, activate your existing virtual environment and install the project's dependencies if needed:

```powershell
py -m pip install reportlab
py -m unittest discover -s tests -v
py -m bookforge_v2.cli --vehicle "My Toyota" --subtitle "Service History" --records 3 --output "output\test_v2.pdf"
```

Open `output\test_v2.pdf` to inspect the generated logbook. The V2 test file adds five tests; the original tests should continue to run unchanged. Run all tests before treating this prototype as verified locally.

## Design principle

A template decides *what content belongs in a book*. The renderer decides *how that content is laid out in a PDF*. This separation should let us add another book type later without duplicating PDF-generation code.
