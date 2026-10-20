# BookForge Lite - Vehicle Maintenance Logbook Generator

A command-line Python application that builds printable, professional PDF logbooks for tracking vehicle service history, mileage, and maintenance records.

## 🌟 Features
* **Custom PDF Generation:** Built using ReportLab to produce styled multi-page printable PDFs.
* **CLI Customization:** Pass flags like `--vehicle`, `--subtitle`, `--records`, and `--output` to customize the book title page and page count.
* **Automated Test Suite:** Built-in unit tests using Python's `unittest` framework to validate inputs and PDF structure.

## 🛠️ Modded Feature
Added support for a `--subtitle` command-line argument via `argparse`, allowing users to specify a custom subtitle that displays dynamically on the PDF title page.

## 🚀 How to Run

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
