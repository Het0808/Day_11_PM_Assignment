# Error Handling Checklist — Day 11 Refactors

---

## Program 1: `part_a_age_calculator.py`
*Original: Day 8 — Variables & User Input*

### Exceptions Caught
| Exception | Why it can happen |
|---|---|
| `ValueError` | `int()` fails if user types letters, symbols, or leaves input blank |
| `ValueError` (custom raise) | Age outside 0–150 is caught manually after conversion |

### Recovery Actions
- Loop continues with `while True` — user keeps getting prompted until they enter something valid
- `else` block only runs on clean input, so partial data never prints

### What the User Sees
```
  Oops — Age 200 is not realistic. Must be between 0 and 150. Please try again.
```
No stack trace, no Python jargon.

### What Gets Logged
```
2024-06-10 14:32:01 - ERROR - Bad age input: Age 200 is not realistic. Must be between 0 and 150.
```
Logged to `age_calculator.log`. The `finally` block logs a debug marker each iteration (invisible to user, useful during development).

---

## Program 2: `part_a_shopping_list.py`
*Original: Day 9 — Lists*

### Custom Exceptions Created
- `EmptyItemError` — raised when item name is blank after `.strip()`
- `DuplicateItemError` — raised when item already exists (case-insensitive check)

### Exceptions Caught
| Exception | Trigger |
|---|---|
| `EmptyItemError` | User hits Enter with no text |
| `DuplicateItemError` | Item already in list |
| `ValueError` | User types letters instead of a number when removing |
| `IndexError` | User picks a number outside the list range |

### Recovery Actions
- Each exception is caught separately at the command loop level
- Program never crashes — always loops back to the `Command:` prompt
- `remove_item()` and `add_item()` raise from inside so they stay reusable

### What the User Sees
```
  Can't do that: Item name cannot be empty.
  Already there: 'Milk' is already in your list.
  Please enter a number for the item to remove.
  Invalid selection: No item #9. List only has 3 items.
```

### What Gets Logged
Warnings logged to `shopping_list.log`. Errors include the actual bad value so debugging is faster.

---

## Program 3: `part_a_grade_calculator.py`
*Original: Day 10 — Functions & Dictionaries*

### Custom Exceptions Created
- `InvalidGradeError` — grade number is valid Python but outside 0–100
- `NoGradesError` — user typed 'done' immediately, no grades collected

### Exceptions Caught
| Exception | Where | Trigger |
|---|---|---|
| `ValueError` | `collect_grades()` | `float()` fails on non-numeric string |
| `InvalidGradeError` | `collect_grades()` | Grade out of 0–100 range |
| `NoGradesError` | `main()` | `calculate_average()` called on empty list |

### Full try/except/else/finally usage
- `try` — calls `parse_grade()`
- `except ValueError` — catches non-numbers
- `except InvalidGradeError` — catches out-of-range numbers
- `else` — appends to list only on success
- `finally` — placeholder for cleanup (e.g. closing a file in a more complex version)

### What the User Sees
```
  'abc' is not a number. Please enter a number between 0 and 100.
  Invalid: Grade must be 0–100, but you entered 105.0.
```

### What Gets Logged (Two-handler Setup)
- **File** (`grade_calculator.log`) — gets DEBUG, INFO, WARNING, ERROR
- **Console** — only WARNING and above (so normal successful grades don't spam the terminal)

```
2024-06-10 14:45:03 [ERROR] Non-numeric grade input: 'abc'
2024-06-10 14:45:08 [ERROR] Out-of-range grade: Grade must be 0–100, but you entered 105.0.
2024-06-10 14:45:15 [INFO] Results — student: Aditya, avg: 87.50, letter: B
```

---

## General Principles Applied Across All Three

1. **No bare `except:`** — every except clause names a specific exception class
2. **User messages vs. log messages are separate** — users see plain English, logs have technical detail
3. **`else` is used intentionally** — only runs when no exception occurred, not just "after try"
4. **`finally` is used for cleanup hooks** — even if stubbed, it shows the structure is understood
5. **Custom exceptions extend `Exception`** and have docstrings explaining when they're raised
