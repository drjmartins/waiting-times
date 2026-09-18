"""
Tests for the shared bounded-retry helper (pipeline_common/retry.py), added
2026-09-18 after the RTT cron failed 2 days running (2026-09-16/17) when NHS/
CloudFront briefly served all 5 RTT FY pages with zero of the expected links
— no HTTP error, just empty content that had cleared by the next day.

Guards:
  1. A transient empty result recovers as soon as fn() returns something
     truthy, without using every available attempt.
  2. A PERSISTENTLY empty result still comes back empty after exactly
     `attempts` tries — the retry rescues a blip, it does not mask a lasting
     failure. The caller's own fail-loud guard is what raises on that.
"""
import pytest

from pipeline_common import retry


def test_retry_recovers_from_transient_empty():
    calls = []
    sleeps = []
    results = iter([[], ["found"]])

    def fn():
        calls.append(1)
        return next(results)

    out = retry.retry_until_nonempty(fn, attempts=3, backoff_seconds=5.0,
                                      sleep_fn=sleeps.append)

    assert out == ["found"]
    assert len(calls) == 2          # recovered on the 2nd attempt, 1 spare left
    assert sleeps == [5.0]          # backed off exactly once, before the retry


def test_retry_gives_up_after_persistent_empty():
    calls = []
    sleeps = []

    def fn():
        calls.append(1)
        return {}

    out = retry.retry_until_nonempty(fn, attempts=3, backoff_seconds=2.0,
                                      sleep_fn=sleeps.append)

    assert out == {}                # still empty -> caller's guard should raise on this
    assert len(calls) == 3          # exhausted all 3 attempts, no more
    assert sleeps == [2.0, 2.0]     # backed off between each attempt (attempts - 1)


def test_retry_calls_on_retry_hook_with_attempt_number_and_backoff():
    seen = []

    def fn():
        return []

    retry.retry_until_nonempty(fn, attempts=3, backoff_seconds=1.5,
                                sleep_fn=lambda s: None,
                                on_retry=lambda attempt, backoff: seen.append((attempt, backoff)))

    assert seen == [(1, 1.5), (2, 1.5)]


def test_retry_first_attempt_success_never_sleeps():
    sleeps = []
    out = retry.retry_until_nonempty(lambda: ["ok"], attempts=3,
                                      sleep_fn=sleeps.append)
    assert out == ["ok"]
    assert sleeps == []


def test_retry_rejects_zero_attempts():
    with pytest.raises(ValueError):
        retry.retry_until_nonempty(lambda: [], attempts=0)
