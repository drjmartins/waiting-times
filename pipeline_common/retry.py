"""
Bounded retry for source-scrape steps that occasionally see a transient
empty/garbled response from an external site.

Both pipelines end their discovery step with a fail-loud "found nothing —
refuse to build" guard. On 2026-09-16/17 the RTT guard tripped because all 5
NHS RTT FY pages returned HTTP 200 with none of the expected zip links — no
exception anywhere (each page fetch has its own try/except and none fired),
just a transient empty-content response from NHS/CloudFront that had cleared
by the next day. The cancer pipeline hits the same NHS domain the same way
and shares the same failure mode risk, it just didn't get unlucky those two
days.

A short, small number of attempts with brief backoff rescues that one-off
case cheaply (the common case still returns on the first attempt with no
delay at all). If the result is STILL empty after every attempt, the empty
result is handed back unchanged so the caller's own fail-loud guard fires —
this helper only buys a transient glitch a couple of extra tries, it must
never suppress a genuine, lasting change (NHS actually renaming, moving, or
removing the source files).
"""
import time

DEFAULT_ATTEMPTS = 3
DEFAULT_BACKOFF_SECONDS = 5.0


def retry_until_nonempty(fn, attempts=DEFAULT_ATTEMPTS,
                          backoff_seconds=DEFAULT_BACKOFF_SECONDS,
                          sleep_fn=time.sleep, on_retry=None):
    """Call `fn()` up to `attempts` times, returning as soon as a call's
    result is truthy. If every attempt comes back falsy (empty dict/list/…),
    returns the last (falsy) result as-is — the caller decides what "refuse
    to build" means for its own guard.

    A raised exception is NOT caught or retried here: a real HTTP error is
    already the caller's job to handle (e.g. per-page try/except around
    individual fetches); this only covers "no exception, but nothing found".
    """
    if attempts < 1:
        raise ValueError("attempts must be >= 1")
    result = fn()
    for attempt in range(2, attempts + 1):
        if result:
            return result
        if on_retry:
            on_retry(attempt - 1, backoff_seconds)
        sleep_fn(backoff_seconds)
        result = fn()
    return result
