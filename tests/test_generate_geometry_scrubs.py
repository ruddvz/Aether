import pytest

from scripts.generate_geometry import _sub_exact_matches


def test_sub_exact_matches_rewrites_single_match_by_default():
    assert _sub_exact_matches(r"stamp=\d+", "stamp=fixed", "x stamp=123 y", label="test") == "x stamp=fixed y"


@pytest.mark.parametrize("text", ["no stamp here", "stamp=1 stamp=2"])
def test_sub_exact_matches_rejects_wrong_default_count(text):
    with pytest.raises(RuntimeError, match=r"expected 1 match\(es\)"):
        _sub_exact_matches(r"stamp=\d+", "stamp=fixed", text, label="test")


def test_sub_exact_matches_accepts_declared_multiple_count():
    assert _sub_exact_matches(
        r"stamp=\d+",
        "stamp=fixed",
        "stamp=1 stamp=2",
        label="test",
        expected_count=2,
    ) == "stamp=fixed stamp=fixed"
