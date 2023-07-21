import pytest
from experiments_lib.expressions.due_date_expr import due_date
from datetime import date
from toolz import first


@pytest.mark.parametrize(
    "test_str, expected_date",
    [
        ("Smlouva o úvěru č. 3364804863 ze dne 26.3.2007", date(2007, 3, 26)),
        ("smlouva o úvěru č. 0353143 ze dne 09.03.2021", date(2021, 3, 9)),
    ],
)
def test_extract(test_str, expected_date):
    match = first(due_date.searchString(test_str))

    assert match
    assert match.date == expected_date
