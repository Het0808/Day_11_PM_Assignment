"""
Day 11 - Part B (Stretch)
file_processor_resilient.py

Reads a directory of CSV files, processes each one, handles failures gracefully,
retries on PermissionError, and exports a JSON report at the end.
"""

import os
import csv
import json
import time
import logging
import traceback
from pathlib import Path


logging.basicConfig(
    filename="file_processor.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(console)

logger = logging.getLogger(__name__)


# ── custom exceptions ────────────────────────────────────────────────────────

class EmptyFileError(Exception):
    """CSV file exists but has no data rows."""
    pass

class BadFormatError(Exception):
    """CSV file is missing required columns."""
    pass


REQUIRED_COLUMNS = {"name", "score", "grade"}


# ── core processing ──────────────────────────────────────────────────────────

def parse_csv(filepath):
    """
    Parse a single CSV file and return a list of row dicts.
    Raises EmptyFileError, BadFormatError, or lets csv.Error bubble up.
    """
    rows = []
    
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        if reader.fieldnames is None:
            raise EmptyFileError(f"{filepath.name} has no headers — file might be empty.")
        
        headers = {h.strip().lower() for h in reader.fieldnames}
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise BadFormatError(
                f"{filepath.name} is missing columns: {missing}. "
                f"Found: {set(reader.fieldnames)}"
            )
        
        for row in reader:
            rows.append(row)
    
    if not rows:
        raise EmptyFileError(f"{filepath.name} has headers but zero data rows.")
    
    return rows


def calculate_aggregates(rows, filename):
    """
    From a list of CSV rows, calculate basic aggregates.
    Returns a dict with count, average score, min, max.
    """
    scores = []
    for i, row in enumerate(rows, 1):
        try:
            score = float(row["score"])
            scores.append(score)
        except (ValueError, KeyError) as e:
            logger.warning("  Row %d in %s has bad score value: %s", i, filename, e)
    
    if not scores:
        return {"count": len(rows), "avg_score": None, "min_score": None, "max_score": None}
    
    return {
        "count": len(rows),
        "avg_score": round(sum(scores) / len(scores), 2),
        "min_score": min(scores),
        "max_score": max(scores),
    }


# ── retry logic ──────────────────────────────────────────────────────────────

def open_with_retry(filepath, max_attempts=3, delay=1):
    """
    Try to parse a file up to max_attempts times.
    Only retries on PermissionError — other errors fail immediately.
    Returns (rows, None) on success, (None, error_info) on final failure.
    """
    last_error = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            rows = parse_csv(filepath)
            if attempt > 1:
                logger.info("  Succeeded on attempt %d for %s", attempt, filepath.name)
            return rows, None
        
        except PermissionError as e:
            last_error = e
            logger.warning(
                "  PermissionError on %s (attempt %d/%d): %s",
                filepath.name, attempt, max_attempts, e
            )
            if attempt < max_attempts:
                logger.info("  Waiting %ds before retry...", delay)
                time.sleep(delay)
        
        except (EmptyFileError, BadFormatError, csv.Error, UnicodeDecodeError, OSError) as e:
            # these won't be fixed by retrying, fail immediately
            return None, e
    
    return None, last_error


# ── main processor ───────────────────────────────────────────────────────────

def process_directory(directory_path):
    """
    Process all CSV files in directory_path.
    Returns a report dict.
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")
    
    csv_files = sorted(directory.glob("*.csv"))
    
    if not csv_files:
        logger.warning("No .csv files found in %s", directory_path)
    
    report = {
        "directory": str(directory.resolve()),
        "total_files_found": len(csv_files),
        "files_processed": 0,
        "files_failed": 0,
        "results": {},
        "error_details": {}
    }
    
    for filepath in csv_files:
        logger.info("Processing: %s", filepath.name)
        
        rows, error = open_with_retry(filepath)
        
        if error is not None:
            # file failed — log full traceback internally, show summary to user
            tb_str = traceback.format_exc()
            logger.error("FAILED: %s\n%s", filepath.name, tb_str)
            
            report["files_failed"] += 1
            report["error_details"][filepath.name] = {
                "error_type": type(error).__name__,
                "message": str(error),
            }
            print(f"  ✗ {filepath.name} — skipped ({type(error).__name__})")
            continue
        
        # success path
        try:
            aggregates = calculate_aggregates(rows, filepath.name)
        except Exception as e:
            logger.error("Aggregation failed for %s: %s", filepath.name, e)
            report["files_failed"] += 1
            report["error_details"][filepath.name] = {
                "error_type": type(e).__name__,
                "message": str(e),
            }
            print(f"  ✗ {filepath.name} — aggregation failed ({e})")
            continue
        
        report["files_processed"] += 1
        report["results"][filepath.name] = aggregates
        print(f"  ✓ {filepath.name} — {aggregates['count']} rows, avg score: {aggregates['avg_score']}")
    
    return report


def save_report(report, output_path="processing_report.json"):
    """Write the report dict to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info("Report saved to %s", output_path)
    print(f"\nReport saved → {output_path}")


# ── entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    directory = sys.argv[1] if len(sys.argv) > 1 else "sample_csvs"
    
    print(f"\n=== Resilient File Processor ===")
    print(f"Reading from: {directory}\n")
    
    try:
        report = process_directory(directory)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}")
        logger.critical("Cannot start processing: %s", e)
        sys.exit(1)
    
    print(f"\nDone — {report['files_processed']} processed, {report['files_failed']} failed.")
    
    save_report(report)
