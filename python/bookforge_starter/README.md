# BookForge Lite — Vehicle Maintenance Logbook Generator

A beginner-friendly Python portfolio project that creates a printable vehicle maintenance logbook PDF. It is a first version of a possible digital-product production tool, not a promise of sales.

## What it demonstrates

- Python functions, input validation, command-line arguments, and file paths
- PDF generation with ReportLab
- Basic automated tests with `unittest`
- Reusable templates and generated output

## Windows setup

1. Install Python 3.11 or newer from https://www.python.org/downloads/windows/.
   During installation, enable **Add Python to PATH**.
2. Extract this project ZIP into a folder, such as `Documents\bookforge_starter`.
3. Open PowerShell in that folder. In File Explorer, open the folder, click the address bar, type `powershell`, and press Enter.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use `py -m pip install -r requirements.txt` and `py -m bookforge` from the same folder instead; activation is convenient but not required.

5. Install the dependency:

   ```powershell
   py -m pip install -r requirements.txt
   ```

## Generate your first PDF

```powershell
py bookforge.py --vehicle "My Toyota" --records 20 --output "output\my_logbook.pdf"
```

Open `output\my_logbook.pdf` to inspect it.

Try a smaller test file first:

```powershell
py bookforge.py --vehicle "Project Car" --records 3 --output "output\test_book.pdf"
```

## Run tests

```powershell
py -m unittest discover -s tests -v
```

The tests check invalid inputs and verify that a PDF is created successfully.

## Suggested next improvements

1. Add configurable book sizes and more page templates.
2. Add a preview image and PDF layout checks.
3. Create a metadata/description draft for each book.
4. Add a duplicate-content checker and a checklist for reviewing every product.
5. Research customer demand and competing products before spending money or publishing at scale.

## Important publishing notes

Inspect the complete PDF and cover against the current Amazon KDP specifications before uploading. This starter creates an interior PDF only; it does not create a KDP cover, upload files, or publish books. Do not copy competitors' text or artwork. If AI generates content or images, follow KDP's current disclosure rules. This tool does not guarantee sales.
