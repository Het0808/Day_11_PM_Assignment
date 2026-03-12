# Day 11 — Exception Handling & Resilient Code

A collection of Python programs and documents covering error handling, retry logic, and interview prep.

---

## Files

| File | Part | Description |
|------|------|-------------|
| `part_a_age_calculator.py` | A | Age calculator with `try/except/else/finally` + logging |
| `part_a_shopping_list.py` | A | Shopping list manager with custom exceptions |
| `part_a_grade_calculator.py` | A | Grade calculator with dual-handler logging setup |
| `error_handling_checklist.md` | A | Documents every exception caught, user messages, and what gets logged |
| `file_processor_resilient.py` | B | Reads a folder of CSVs, retries on `PermissionError`, exports `processing_report.json` |
| `day11_part_c.md` | C | Interview Q&A — execution flow, `safe_json_load`, and bug fixes |
| `day11_part_d.py` | D | AI-generated `@retry` decorator, 3 tests, and critical evaluation |

---

## Key Concepts Covered

- `try / except / else / finally` structure
- Specific exceptions over bare `except:`
- Custom exception classes
- Logging to file vs. console
- Retry logic with exponential backoff
- `functools.wraps` for decorator metadata
