# BookForge v3 — complete six-chapter workbook assembly

The v3 pipeline builds on the existing v2 renderer. It supports two themes, sequential chapters, repair tickets, answer keys at the end and PDF preflight.

Run from repository root:

```powershell
py -m pip install -r bookforge_v2/requirements.txt
py bookforge_v3/pipeline.py bookforge_v3/data/mistake_mechanics_six_chapters.json --theme clean-premium --output clean.pdf
py bookforge_v3/pipeline.py bookforge_v3/data/mistake_mechanics_six_chapters.json --theme playful-illustrated --output playful.pdf
py -m unittest discover -s bookforge_v3/tests -v
```

Install DejaVu Sans regular and bold according to the v2 README. Dataset exercises are curated examples adapted from the original workbook, **not a complete transcription** and **not independently curriculum-audited**. Publishing is not automated.
