import logging

# two handlers: file gets full details, console only shows WARNING+
logger = logging.getLogger("grade_calculator")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("grade_calculator.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter("%(message)s"))

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class InvalidGradeError(Exception):
    """Grade is outside the allowed 0–100 range."""
    pass


class NoGradesError(Exception):
    """Tried to calculate average with an empty grade list."""
    pass


def parse_grade(raw_input):
    """
    Convert string input to a valid grade (float, 0-100).
    Raises ValueError or InvalidGradeError.
    """
    grade = float(raw_input)  # raises ValueError if not a number
    if grade < 0 or grade > 100:
        raise InvalidGradeError(f"Grade must be 0–100, but you entered {grade}.")
    return grade


def calculate_average(grades):
    """Return average of grades list. Raises NoGradesError if empty."""
    if not grades:
        raise NoGradesError("Cannot calculate average — no grades were entered.")
    return sum(grades) / len(grades)


def letter_grade(avg):
    """Return letter grade string for a numeric average."""
    if avg >= 90: return "A"
    if avg >= 80: return "B"
    if avg >= 70: return "C"
    if avg >= 60: return "D"
    return "F"


def collect_grades():
    """
    Prompt user to enter grades one by one.
    Returns a list of valid floats.
    """
    grades = []
    print("Enter grades one at a time. Type 'done' when finished.\n")
    
    while True:
        raw = input(f"  Grade #{len(grades)+1} (or 'done'): ").strip()
        
        if raw.lower() == "done":
            break
        
        try:
            grade = parse_grade(raw)
        
        except ValueError:
            logger.error("Non-numeric grade input: '%s'", raw)
            print(f"  '{raw}' is not a number. Please enter a number between 0 and 100.")
            continue
        
        except InvalidGradeError as e:
            logger.error("Out-of-range grade: %s", e)
            print(f"  Invalid: {e}")
            continue
        
        else:
            grades.append(grade)
            logger.debug("Grade accepted: %s", grade)
        
        finally:
            pass  # could close a file handle or flush a buffer here
    
    return grades


def main():
    print("=== Grade Calculator ===\n")
    
    student_name = input("Student name: ").strip() or "Unknown Student"
    
    grades = collect_grades()
    
    try:
        avg = calculate_average(grades)
    
    except NoGradesError as e:
        logger.warning("No grades provided for '%s': %s", student_name, e)
        print(f"\n  {e}")
        print("  Exiting without results.")
        return
    
    else:
        letter = letter_grade(avg)
        print(f"\n--- Results for {student_name} ---")
        print(f"  Grades entered : {[round(g, 1) for g in grades]}")
        print(f"  Average        : {avg:.2f}")
        print(f"  Letter grade   : {letter}")
        logger.info("Results — student: %s, avg: %.2f, letter: %s", student_name, avg, letter)
    
    finally:
        print("\n(Grade session ended.)")


if __name__ == "__main__":
    main()
