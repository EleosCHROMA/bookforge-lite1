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
```
## Preview
<img width="1126" height="222" alt="tests1" src="https://github.com/user-attachments/assets/d6fd1a08-1d6a-4fc6-af9c-4af328c7798c" />
<img width="796" height="865" alt="test_book" src="https://github.com/user-attachments/assets/d8b4b876-0bfa-492c-8cac-72578b4a8708" />

