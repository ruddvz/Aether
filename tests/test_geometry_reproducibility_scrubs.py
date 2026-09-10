import pytest

from scripts.generate_geometry import scrub_exact


def test_scrub_exact_replaces_one_expected_match():
    source = "prefix BUILD @ 2026-09-10T12:00:00 suffix"
    result = scrub_exact(
        source,
        r"BUILD @ \S+",
        "BUILD @ 2026-09-03T00:00:00",
        "test timestamp",
    )
    assert result == "prefix BUILD @ 2026-09-03T00:00:00 suffix"


@pytest.mark.parametrize(
    "source,found",
    [
        ("no timestamp here", 0),
        ("BUILD @ first BUILD @ second", 2),
    ],
)
def test_scrub_exact_rejects_missing_or_duplicate_matches(source, found):
    with pytest.raises(RuntimeError, match=rf"expected 1 match\(es\), found {found}"):
        scrub_exact(source, r"BUILD @ \S+", "BUILD @ fixed", "test timestamp")
