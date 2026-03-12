"""
Prompt given to AI:
    Write a Python decorator called @retry(max_attempts=3, delay=1)
    that automatically retries a function if it raises an exception,
    with exponential backoff. The decorator should use functools.wraps
    to preserve the original function's metadata, and should distinguish
    between retryable and non-retryable exceptions.
"""

import time
import random
import functools
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# ── AI-Generated Decorator ────────────────────────────────────────────────────

def retry(max_attempts=3, delay=1, retryable_exceptions=(Exception,), non_retryable_exceptions=()):
    """
    Decorator that retries a function on failure with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including the first try).
        delay: Initial delay in seconds between retries (doubles each attempt).
        retryable_exceptions: Tuple of exception types that trigger a retry.
        non_retryable_exceptions: Tuple of exception types that should never be retried.
    """
    def decorator(func):
        @functools.wraps(func)  # preserves __name__, __doc__, etc.
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except non_retryable_exceptions as e:
                    logger.error("Non-retryable error in %s: %s", func.__name__, e)
                    raise  # re-raise immediately, no retry

                except retryable_exceptions as e:
                    last_exception = e
                    logger.warning(
                        "%s failed (attempt %d/%d): %s",
                        func.__name__, attempt, max_attempts, e
                    )
                    if attempt < max_attempts:
                        logger.info("Retrying in %.1fs...", current_delay)
                        time.sleep(current_delay)
                        current_delay *= 2  # exponential backoff

            logger.error("%s failed after %d attempts.", func.__name__, max_attempts)
            raise last_exception

        return wrapper
    return decorator


# ── Test 1: Function that fails ~50% of the time ──────────────────────────────

@retry(max_attempts=5, delay=0.1)  # short delay so tests run fast
def flaky_operation():
    """
    Simulates an unreliable operation that fails 50% of the time.
    Example: a network request, a file lock, an API call.
    """
    if random.random() < 0.5:
        raise ConnectionError("Simulated connection failure")
    return "Success!"


# ── Test 2: Non-retryable exception should fail immediately ───────────────────

@retry(
    max_attempts=3,
    delay=0.1,
    retryable_exceptions=(ConnectionError,),
    non_retryable_exceptions=(ValueError,)
)
def validated_operation(x):
    """Only accepts positive numbers — ValueError is programmer error, not transient."""
    if x < 0:
        raise ValueError(f"Expected positive number, got {x}")
    if random.random() < 0.4:
        raise ConnectionError("Transient network issue")
    return x * 2


# ── Test 3: Verify functools.wraps preserved metadata ────────────────────────

def check_metadata():
    print(f"  Function name : {flaky_operation.__name__}")   # should be 'flaky_operation'
    print(f"  Docstring     : {flaky_operation.__doc__.strip()}")


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 55)
    print("TEST 1 — Flaky operation (fails ~50% of the time)")
    print("=" * 55)
    for run in range(3):
        try:
            result = flaky_operation()
            print(f"  Run {run+1}: {result}\n")
        except ConnectionError:
            print(f"  Run {run+1}: Failed even after all retries.\n")

    print("=" * 55)
    print("TEST 2 — Non-retryable ValueError fails immediately")
    print("=" * 55)
    try:
        validated_operation(-5)
    except ValueError as e:
        print(f"  Raised immediately (no retry): {e}\n")

    print("  Now testing retryable ConnectionError...")
    try:
        result = validated_operation(10)
        print(f"  Result: {result}\n")
    except ConnectionError:
        print("  Still failed after retries.\n")

    print("=" * 55)
    print("TEST 3 — functools.wraps metadata check")
    print("=" * 55)
    check_metadata()
    print()

    # ── Critical Evaluation (200 words) ──────────────────────────────────────
    print("=" * 55)
    print("CRITICAL EVALUATION")
    print("=" * 55)
    evaluation = """
Does it handle edge cases?
    Mostly yes. max_attempts=1 works correctly — tries once,
    raises immediately on failure. An empty non_retryable_exceptions=()
    tuple also works fine since except () matches nothing in Python.
    One real gap: if delay=0 and max_attempts is large, you'd hammer
    a failing service with no breathing room. Production code should
    enforce a minimum delay or add random jitter.

Does it preserve function metadata with functools.wraps?
    Yes — Test 3 confirms __name__ and __doc__ are intact. Without
    functools.wraps, every decorated function would show up as 'wrapper'
    in logs and stack traces, making debugging a nightmare.

Does it distinguish retryable vs. non-retryable exceptions?
    Yes, cleanly. non_retryable_exceptions re-raises immediately without
    any sleep or retry. This is the right design — a ValueError from bad
    input will never be fixed by retrying, but a ConnectionError might
    succeed on the next attempt since it's caused by a transient condition.

What improvements would I make?
    1. Add jitter (delay * random.uniform(0.5, 1.5)) so distributed
       systems don't all retry simultaneously — this is the thundering
       herd problem and it makes outages worse.
    2. Add an on_retry callback so callers can hook in logic before each
       retry, e.g. refreshing an expired auth token.
    3. Remove the default retryable_exceptions=(Exception,). Catching
       Exception broadly is nearly as bad as bare except — it includes
       MemoryError and RecursionError which should never be retried.
       Better to force the caller to be explicit.
    4. Add a max_delay cap so exponential backoff doesn't grow to absurd
       wait times on the 10th retry of a long-running job.
"""
    print(evaluation)
