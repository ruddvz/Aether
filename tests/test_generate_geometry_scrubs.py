import pytest

from scripts.generate_geometry import _sub_exactly_once


def test_sub_exactly_once_rewrites_single_match():
    assert _sub_exactly_once(r"stamp=\d+", "stamp=fixed", "x stamp=123 y", label="test") == "x stamp=fixed y"


@pytest.mark.parametrize("text", ["no stamp here", "stamp=1 stamp=2"])
def test_sub_exactly_once_rejects_missing_or_duplicate_matches(text):
    with pytest.raises(RuntimeError, match="expected exactly one match"):
        _sub_exactly_once(r"stamp=\d+", "stamp=fixed", text, label="test")
