import pytest

from scripts.generate_geometry import sub_exactly_once


def test_timestamp_scrub_requires_exactly_one_marker():
    assert sub_exactly_once("timestamp", "fixed", "before timestamp after", "test marker") == "before fixed after"

    with pytest.raises(RuntimeError, match="Expected exactly one test marker timestamp marker, found 0"):
        sub_exactly_once("timestamp", "fixed", "marker missing", "test marker")


def test_timestamp_scrub_does_not_hide_multiple_markers():
    # count=1 makes the replacement bounded; a duplicated source marker must still be
    # surfaced explicitly rather than leaving a second wall-clock value behind.
    with pytest.raises(RuntimeError, match="found 2"):
        sub_exactly_once("timestamp", "fixed", "timestamp and timestamp", "test marker")
