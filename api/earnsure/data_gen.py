"""Deterministic demo dataset (TD §6). Built once per process and cached."""

from datetime import date, timedelta
from functools import lru_cache

import numpy as np

from . import config

WEEKLY_INCOME = [820, 880, 790, 910, 860, 840, 930, 800, 780, 870,
                 420, 450, 480,
                 700, 1150, 1220, 1180,
                 850, 900, 860, 810, 780, 870, 840, 880, 900]

WEEKLY_DISCRETIONARY = [320, 368, 551, 451, 221, 384, 323, 400, 224, 409,
                        409, 543, 417, 436, 236, 610, 193, 495, 352, 297,
                        319, 318, 423, 374, 533, 202]

EXAM_WEEKS = {10, 11, 12}
TARGET_TXN_COUNT = 612

DISCRETIONARY_MERCHANTS = [
    ("FRESHMART GROCERIES", "FRESHMART"),
    ("METRO TRANSIT TOPUP", "METRO TRANSIT"),
    ("CORNER BAKERY CO", "CORNER BAKERY"),
    ("NOODLE HOUSE CBD", "NOODLE HOUSE"),
    ("PHARMACARE CHEMIST", "PHARMACARE"),
    ("CAMPUS COFFEE CART", "CAMPUS COFFEE"),
    ("GREENLEAF MARKET", "GREENLEAF"),
    ("BOOKNOOK STATIONERY", "BOOKNOOK"),
    ("SPICE ROAD TAKEAWAY", "SPICE ROAD"),
    ("LAUNDRY LANE", "LAUNDRY LANE"),
]


def week_start(i: int) -> date:
    return config.PERIOD_START + timedelta(weeks=i)


def _split_exact(total: float, n: int, rng) -> list[float]:
    """Split `total` into n positive cent amounts that sum exactly to it."""
    weights = rng.uniform(0.4, 1.6, n)
    cents = np.floor(weights / weights.sum() * round(total * 100)).astype(int)
    cents[0] += round(total * 100) - cents.sum()
    return [c / 100 for c in cents]


@lru_cache(maxsize=1)
def build() -> list[dict]:
    rng = np.random.default_rng(2026)
    rows: list[dict] = []

    def add(d: date, desc: str, amount: float, counterparty: str, account: str = "acc_everyday"):
        rows.append({"account_id": account, "date": d, "description": desc,
                     "amount": round(float(amount), 2), "counterparty": counterparty})

    # --- Income (TD §6.1) ------------------------------------------------------
    cafe = {}  # week -> amount, fortnightly on Thursdays
    for i in range(0, config.N_WEEKS, 2):
        cafe[i] = 300.0 if i in EXAM_WEEKS else float(rng.integers(585, 616))
    # Freelance goes in the six highest-income weeks without a café pay day,
    # which keeps the delivery remainder as small as possible.
    non_cafe = sorted((i for i in range(config.N_WEEKS) if i not in cafe),
                      key=lambda i: -WEEKLY_INCOME[i])
    freelance = {i: float(rng.integers(530, 551)) for i in sorted(non_cafe[:6])}

    for n, i in enumerate(sorted(freelance)):
        # Invoices clear mid-week (Wednesday)
        add(week_start(i) + timedelta(days=2), f"INV-10{41 + n} STUDIO MOSS", freelance[i], "STUDIO MOSS")
    for i, amt in cafe.items():
        add(week_start(i) + timedelta(days=3), "BEAN&BRICK CAFE PAY", amt, "BEAN & BRICK CAFE")
    for i in range(config.N_WEEKS):
        payout = WEEKLY_INCOME[i] - cafe.get(i, 0) - freelance.get(i, 0)
        assert payout > 0, (i, payout)
        add(week_start(i), "QUICKDROP DELIVERY PAYOUT", payout, "QUICKDROP")

    # --- Regular outgoings (TD §6.2) --------------------------------------------
    months = [date(2026, m, 1) for m in range(4, 10)]  # Apr..Sep
    for i in range(config.N_WEEKS):
        add(week_start(i), "RENT PAYID TO J SMITH PROPERTY", -210, "J SMITH PROPERTY")
    for m in months:
        add(m, "WISE TRANSFER INTL", -200, "WISE TRANSFER INTL")
        add(m.replace(day=5), "STREAMFLIX SUBSCRIPTION", -15, "STREAMFLIX")
        add(m.replace(day=12), "SOUNDBOX PREMIUM", -11, "SOUNDBOX")
        add(m.replace(day=10), "SPARKGRID ENERGY BILL", -80, "SPARKGRID ENERGY")
        add(m.replace(day=15), "NBNLINK INTERNET", -50, "NBNLINK")
        add(m.replace(day=20), "TELCO MOBILE PLAN", -45, "TELCO MOBILE")
    for i in range(0, config.N_WEEKS, 2):
        add(week_start(i) + timedelta(days=4), "PAYLATER REPAY", -30, "PAYLATER")

    # --- Not counted as income (TD §6.3) -----------------------------------------
    for i in range(14):
        d = week_start(i * 26 // 14) + timedelta(days=1)
        add(d, "TRANSFER TO SAVINGS", -200, "OWN ACCOUNT", "acc_everyday")
        add(d, "TRANSFER FROM EVERYDAY", 200, "OWN ACCOUNT", "acc_savings")
    add(date(2026, 5, 6), "REFUND HOMEWARES STORE", 58, "HOMEWARES STORE")
    add(date(2026, 8, 19), "REFUND ONLINE ORDER", 38, "ONLINE ORDER")

    # --- Items needing confirmation (TD §6.4) --------------------------------------
    add(date(2026, 8, 14), "FROM T NGUYEN", 250, "T NGUYEN")
    add(date(2026, 7, 3), "OSKO FROM M PATEL REF THANKS", 120, "M PATEL")
    add(date(2026, 9, 22), "PAYID FROM A OKAFOR", 85, "A OKAFOR")

    # --- Discretionary card spending (TD §6.5), padded to the target count --------
    remaining = TARGET_TXN_COUNT - len(rows)
    per_week = [remaining // config.N_WEEKS] * config.N_WEEKS
    for i in range(remaining % config.N_WEEKS):
        per_week[i * 2 % config.N_WEEKS] += 1
    for i, n in enumerate(per_week):
        for amt in _split_exact(WEEKLY_DISCRETIONARY[i], n, rng):
            desc, cp = DISCRETIONARY_MERCHANTS[int(rng.integers(len(DISCRETIONARY_MERCHANTS)))]
            add(week_start(i) + timedelta(days=int(rng.integers(0, 7))), desc, -amt, cp)

    rows.sort(key=lambda r: (r["date"], r["account_id"], r["description"]))
    for n, r in enumerate(rows, 1):
        r["txn_id"] = f"t{n:04d}"
    return rows


def week_index(d: date) -> int:
    return (d - config.PERIOD_START).days // 7
