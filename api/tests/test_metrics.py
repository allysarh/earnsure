from earnsure import classify, fmt, metrics, trends


def test_demo_figures():
    s = metrics.summary(metrics.analyse())
    assert s["dependable"] == 790
    assert s["typical"] == 855
    assert abs(s["regular_outflows"] - 317.54) <= 0.01
    assert fmt.money(s["regular_outflows"])["display"] == "$318"
    assert fmt.money(s["typical_left"])["display"] == "$537"
    assert fmt.money(s["lowest_left"])["display"] == "$102"
    assert fmt.one_dp(s["buffer_weeks"])["display"] == "3.7"
    assert s["status"] == "Watch"


def test_safe_to_spend():
    s = metrics.summary(metrics.analyse())
    assert fmt.money(s["top_up"])["display"] == "$79"
    assert fmt.money(s["safe"])["display"] == "$393"


def test_confirming_work_recalculates():
    t_nguyen = classify.confirmation_queue(list(metrics.base_classified()))[0]
    before = metrics.analyse()
    after = metrics.analyse({t_nguyen["txn_id"]: "work_income"})
    assert after.weekly_income.sum() == before.weekly_income.sum() + 250
    assert metrics.dependable(after.weekly_income) >= metrics.dependable(before.weekly_income)
    assert metrics.analyse({t_nguyen["txn_id"]: "one_off_personal"}).weekly_income.sum() == before.weekly_income.sum()
    assert metrics.analyse({t_nguyen["txn_id"]: "other_in"}).weekly_income.sum() == before.weekly_income.sum()


def test_regular_family_support_counts_as_income():
    t_nguyen = classify.confirmation_queue(list(metrics.base_classified()))[0]
    before = metrics.analyse()
    after = metrics.analyse({t_nguyen["txn_id"]: "family_support"})
    assert after.weekly_income.sum() == before.weekly_income.sum() + 250
    assert metrics.dependable(after.weekly_income) >= metrics.dependable(before.weekly_income)
    # Not a recurring earnings stream, so it doesn't appear on the "Money coming in" list
    assert len(classify.income_streams(after.txns)) == 3


def test_lean_period_and_recovery():
    p = trends.describe_period(trends.lean_periods(metrics.analyse().weekly_income)[0])
    assert p["range"] == "8 – 28 Jun" and p["weeks"] == 3
    assert p["weeks_to_recover"] == 4 and p["recovered_by"] == "6 Jul"


def test_half_up_rounding():
    assert fmt.pct(0.895)["display"] == "90%"
    assert fmt.money(2.5)["display"] == "$3"
