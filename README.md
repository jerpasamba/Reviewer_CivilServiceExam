# CSC Civil Service Exam Reviewer

A static, browser-based review app for the Philippine **Civil Service Examination (CSE)**. No servers, no frameworks, no installation — just open the HTML file (or use the GitHub Pages link below) and start reviewing.

## Quizzes included

| File | Content | Items |
| ---- | ------- | ----- |
| `quiz.html` | Full combined reviewer (2026) — all topics | 681 |
| `quiz-2018.html` | Actual CSE 2018 exam set (Professional) | 189 |
| `quiz-2019.html` | Actual CSE 2019 exam set (Professional) | 193 |
| `quiz-2020.html` | Actual CSE 2020 exam set (Professional) | 170 |

### Topics covered

- **Mathematics** — Math Word Problems (73), Data Sufficiency (20)
- **Clerical Operations** — Alphabetizing (20)
- **English Vocabulary** — Synonyms (40), Antonyms (38)
- **English & Reading** — Single/Double Word Analogy (80), Identifying Errors (60), Paragraph Development (10), Correct Usage (40), Reading Comprehension (50)
- **Filipino** — Kasingkahulugan (25), Kasalungat (25), Kawikaan (25), Wastong Gamit (30), Pagkilala sa Mali (25), Pag-unawa sa Binasa (30), Pagtatalata (10)
- **Civics / General Information** — Constitution (30)
- **Abstract Reasoning** — Inductive Reasoning (50)

## Features

- **Practice mode** — answer questions by topic and see the correct answer immediately.
- **Mock exam mode** — simulates the real exam:
  - Professional: 170 items / 190 minutes
  - Subprofessional: 165 items / 160 minutes
- **Dark mode** toggle.
- **Progress tracking** — answers are saved automatically in your browser (`localStorage`), so you can resume anytime.
- **Answer key embedded** — every question is graded instantly.

## Getting started

- **Online:** open <https://jerpasamba.github.io/Reviewer_CivilServiceExam/>
- **Locally:** download any of the `quiz*.html` files and double-click to open in your browser. No internet needed.

## How it works

Each quiz is a single self-contained HTML file with the question bank, grading logic, and UI all in one. The per-year quizzes are generated from the source PDFs by the Python scripts in this repo:

- `parse_years.py` — parses the CSE 2018/2019/2020 PDFs into `parsed_years.json`.
- `gen_years.py` — renders `quiz-2018.html`, `quiz-2019.html`, `quiz-2020.html` from the `quiz.html` template.
- `fix_math.py` — repairs malformed math questions (missing operators, garbled options) in `quiz.html`.

### Data quality notes

- Where the source PDFs contained OCR/extraction errors (missing math operators, merged or duplicate options, truncated wording), the questions were corrected against the original print sources.
- A few source questions are genuinely incomplete (missing answer keys or mangled layouts that could not be reconstructed, e.g. two items in the base bank's Antonyms section) and are kept as-is.

## License

Review content is compiled from public Civil Service Exam review materials for personal study. Use at your own discretion.
