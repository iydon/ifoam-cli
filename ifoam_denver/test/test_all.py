import doctest

from ifoam_denver import template


def test_template() -> None:
    ans = doctest.testmod(template)
    assert ans.failed == 0
