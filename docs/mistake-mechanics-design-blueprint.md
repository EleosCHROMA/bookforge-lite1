# Mistake Mechanics — BookForge v2 Design Blueprint

Source: user-supplied `Mistake_Mechanics_Styled_Interior(2).pdf` (26 pages, US Letter, 612 × 792 pt). Reference only; do not overwrite source.

## Observed structure
- Chapter 1 Decimal Diagnostics: pp. 1–5.
- Chapter 2 Ratios, Rates & Percents: pp. 6–9.
- Chapter 3 Expressions & Equations: pp. 10–12.
- Chapter 4 Rational Numbers & Coordinate Plane: pp. 13–15.
- Chapter 5 Area, Surface Area & Volume: pp. 16–18.
- Chapter 6 Statistics & Data Analysis: pp. 19–21.
- Master Mechanic Guide / answer keys: pp. 22–26.

## Reusable page components
1. Chapter opener: color-coded number, chapter title, introductory theme and learning goals.
2. Lesson section: explanatory rule, worked examples, optional vertical math setup.
3. Two-column practice grid: numbered questions, bordered/dashed WORK AREA.
4. Repair ticket: colored top bar, customer/faulty work, diagnosed error, green MY REPAIR workspace; topic-specific color.
5. Quiz page: two-column numbered questions, no visible answers.
6. Answer-key pages: chapter-grouped solutions with alternating lightly tinted rows; located exclusively after all chapter content.
7. Running header/footer: chapter/topic, series name, page number.

## Style tokens to extract and implement
- US Letter portrait, minimum 0.5-inch safe content margin.
- Typography: embedded Poppins Bold/Medium and DejaVu Sans variants seen in source; avoid unembedded Helvetica in final PDFs.
- Chapter colors vary by section (orange, blue, purple, green, pink, teal).
- White background; rounded boxes; dotted/dashed work-area borders; high contrast.
- Do not copy fixed text as drawing commands: content comes from validated JSON.

## v2 milestone: two-page generator
- Page 1: chapter opener and goals.
- Page 2: two-column worksheet with numbered exercises and workspace.
- Input: JSON schema for book metadata, chapter title, objectives, problems, optional hints and answer IDs.
- Output: deterministic PDF with exact 2-page assertion, no clipped text, and safe margins.
- Validation: required fields; long-text overflow handling; missing-glyph and embedded-font checks; answer mapping; repeatable tests.
- Keep the existing `main` branch unchanged until tests and user review.

## Follow-on milestones
- Repair-ticket component and multi-page chapters.
- Answer key collected at end of book.
- Arithmetic verification and human editorial review before KDP production.
- Configurable trim, bleed, typography, palettes, and book genre.

## Issues observed in source to avoid reproducing
- Several pages have large unused lower sections, particularly page 8.
- Source PDF font resources include a nonembedded Helvetica Type1 reference; final output should eliminate or embed any such references.
- Some math notation in extracted text is ambiguous (superscripts and mixed fractions); preserve true typeset notation and inspect rendered results.
- Review educational correctness before reuse; source is a visual reference, not a verified question bank.

## Acceptance criteria
1. Generator accepts a sample JSON input and produces exactly two US Letter pages.
2. Page 1 and page 2 visually resemble the source's opener and practice cards.
3. All text remains within safe margins, with no overlaps or clipping.
4. Tests pass on Windows and CI.
5. All fonts are embedded and math symbols render correctly.
6. Only `version-2` is modified; `main` remains untouched.
