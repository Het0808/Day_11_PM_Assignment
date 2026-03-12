# Day 11 — Part C: Interview Ready

---

## Q1 — Conceptual: Execution Flow of try / except / else / finally

**When does each block run?**

- `try` — always runs first. This is where you put code that *might* fail.
- `except` — only runs if the `try` block raised an exception. If no exception occurred, this block is skipped entirely.
- `else` — only runs if `try` completed *without* raising an exception. Think of it as the success path. Putting code here instead of the end of `try` makes it explicit that this code only executes when nothing went wrong.
- `finally` — runs no matter what. Even if an exception was raised and not caught, even if there's a `return` or `break` inside `try` or `except`. This is where cleanup code lives — closing files, releasing locks, flushing buffers.

**What if an exception occurs inside the `else` block?**

It propagates normally. The `except` for *this* try/except does NOT catch it, because `else` is outside the `try` scope. The exception bubbles up to the nearest enclosing try/except higher in the call stack.

### Code Example — All Four Blocks Together

```python
def divide(a, b):
    print(f"Trying to divide {a} / {b}")

    try:
        result = a / b              # ZeroDivisionError if b == 0

    except ZeroDivisionError:
        print("  [except] Can't divide by zero!")
        result = None

    else:
        # only reaches here if no exception was raised
        print(f"  [else] Division succeeded: {result:.2f}")

    finally:
        # always runs — good for cleanup
        print("  [finally] Done with this attempt.\n")

    return result


# Run 1: no exception — try → else → finally
divide(10, 2)
# Output:
#   Trying to divide 10 / 2
#   [else] Division succeeded: 5.00
#   [finally] Done with this attempt.

# Run 2: exception — try → except → finally (else is skipped)
divide(10, 0)
# Output:
#   Trying to divide 10 / 0
#   [except] Can't divide by zero!
#   [finally] Done with this attempt.
```

### Demonstrating: Exception in else Does NOT Get Caught by the except Above

```python
def demo_else_exception():
    try:
        x = 5                      # no exception here
    except ValueError:
        print("This won't run")
    else:
        print("try succeeded, now in else...")
        raise RuntimeError("Exception raised inside else — watch it propagate!")
    finally:
        print("finally still runs even when else raises")


try:
    demo_else_exception()
except RuntimeError as e:
    print(f"Caught by OUTER try/except: {e}")

# Output:
#   try succeeded, now in else...
#   finally still runs even when else raises
#   Caught by OUTER try/except: Exception raised inside else — watch it propagate!
```

---

## Q2 — Coding: `safe_json_load(filepath)`

```python
import json
import logging

logging.basicConfig(
    filename="json_loader.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(funcName)s — %(message)s"
)
logger = logging.getLogger(__name__)


def safe_json_load(filepath):
    """
    Safely read a JSON file and return its contents as a dict.

    Returns:
        dict: Parsed JSON data on success.
        None: If any error occurs (file missing, bad JSON, no permission).

    All errors are logged to json_loader.log.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

    except FileNotFoundError:
        logger.error("File not found: %s", filepath)
        return None

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s — %s (line %d, col %d)",
                     filepath, e.msg, e.lineno, e.colno)
        return None

    except PermissionError:
        logger.error("Permission denied reading: %s", filepath)
        return None

    else:
        return data
```

### Tests

```python
import tempfile, os

# Test 1: valid JSON
with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump({"name": "Aditya", "score": 95}, f)
    valid_path = f.name

print("Test 1 (valid)   :", safe_json_load(valid_path))
# → {'name': 'Aditya', 'score': 95}

# Test 2: corrupted JSON
with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    f.write("{name: missing quotes}")
    bad_path = f.name

print("Test 2 (bad JSON):", safe_json_load(bad_path))
# → None  (error logged to json_loader.log)

# Test 3: file doesn't exist
print("Test 3 (missing) :", safe_json_load("/nonexistent/data.json"))
# → None  (error logged to json_loader.log)

os.unlink(valid_path)
os.unlink(bad_path)
```

---

## Q3 — Debug: Fix the Buggy `process_data` Function

### Original Broken Code

```python
def process_data(data_list):
    results = []
    for item in data_list:
        try:
            value = int(item)
            results.append(value * 2)
        except:
            print("Error occurred")
            continue
        finally:
            return results   # BUG
    return results
```

### Three Bugs Identified

**Bug 1 — Bare `except:`**

Catches literally everything, including `KeyboardInterrupt` and `SystemExit`. These are not normal program errors — catching them silently means the user can't even stop the program with Ctrl+C. Should be `except (ValueError, TypeError)` so only expected conversion errors are caught and serious signals still propagate.

**Bug 2 — `return` inside `finally`**

`finally` runs after *every single loop iteration*, not at the end of the whole loop. So the function returns after processing the very first item in the list, ignoring every item after it. The `return` belongs outside the loop entirely.

**Bug 3 — Vague error message**

`print("Error occurred")` tells nobody anything useful. Which item failed? What was the error type? What was the actual exception message? Should include the item value and the exception itself so failures can be diagnosed.

### Fixed Version

```python
def process_data(data_list):
    """
    Convert each item in data_list to int and double it.
    Skips items that can't be converted, with a clear message for each.
    """
    results = []

    for item in data_list:
        try:
            value = int(item)
            results.append(value * 2)

        except (ValueError, TypeError) as e:
            # specific exceptions only — KeyboardInterrupt etc. still propagate
            print(f"Skipping '{item}': could not convert to int — {e}")
            continue

        # finally removed from inside the loop
        # cleanup code could go here, but never a return

    return results   # return once, after the full loop completes


# Test
test_data = ["3", "7", "abc", None, "10", "2.5", "4"]
output = process_data(test_data)
print("Results:", output)
# Skipping 'abc': could not convert to int — invalid literal for int() with base 10: 'abc'
# Skipping 'None': could not convert to int — int() argument must be a string...
# Skipping '2.5': could not convert to int — invalid literal for int() with base 10: '2.5'
# Results: [6, 14, 20, 8]
```
