import pytest

from earnsure import affordability, metrics


@pytest.mark.parametrize("rent, share, rate, raw, label", [
    (230, "29%", "94%", 0.9385, "Likely affordable"),
    (250, "32%", "90%", 0.8950, "Possible, some risk"),
    (290, "37%", "79%", 0.7935, "Unlikely"),
])
def test_rent_checks(rent, share, rate, raw, label):
    r = affordability.check(metrics.analyse(), rent, "Weekly", "Rent")
    assert r["share"]["display"] == share
    assert r["sim_pass_rate"]["display"] == rate
    assert r["sim_pass_rate"]["value"] == raw
    assert r["label"] == label


def test_weekly_cost():
    assert affordability.weekly_cost(460, "Fortnightly") == 230
    assert affordability.weekly_cost(52, "Monthly") == 12
