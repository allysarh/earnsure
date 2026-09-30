from datetime import date

from earnsure import classify, data_gen, metrics


def test_transaction_count():
    assert abs(len(data_gen.build()) - 612) <= 10


def test_weekly_income_matches_spec():
    a = metrics.analyse()
    assert a.weekly_income.tolist() == data_gen.WEEKLY_INCOME


def test_income_streams():
    streams = {s["key"]: s for s in classify.income_streams(metrics.analyse().txns)}
    cafe, gig, free = streams["work_income"], streams["gig_income"], streams["freelance_income"]
    assert cafe["frequency"] == "Every fortnight" and cafe["count"] == 13 and abs(cafe["typical"] - 600) <= 15
    assert gig["frequency"] == "Weekly" and gig["count"] == 26
    assert free["count"] == 6 and abs(free["typical"] - 540) <= 15
    assert "monthly" in free["frequency"].lower()


def test_outgoing_streams_weekly_total():
    outs = classify.outgoing_streams(metrics.analyse().txns)
    assert [s["key"] for s in outs] == classify.BILL_CATEGORIES
    assert abs(sum(s["weekly_equivalent"] for s in outs) - 317.54) <= 0.01


def test_not_counted():
    nc = classify.not_counted(metrics.analyse().txns)
    assert nc["transfers"] == {"count": 14, "total": 2800}
    assert nc["refunds"] == {"count": 2, "total": 96}


def test_confirmation_queue():
    q = classify.confirmation_queue(list(metrics.base_classified()))
    assert len(q) == 3
    assert q[0]["description"] == "FROM T NGUYEN" and q[0]["amount"] == 250 and q[0]["date"] == date(2026, 8, 14)
    assert all(not t["counts_as_income"] for t in q)
