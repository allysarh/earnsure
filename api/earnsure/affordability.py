"""Affordability check: share of dependable income + block bootstrap (TD §7.6)."""

import numpy as np

from . import config, data_gen, fmt, metrics

TYPES = ("Rent", "Phone plan", "Loan repayment")
FREQUENCIES = ("Weekly", "Fortnightly", "Monthly")
LABELS = {2: ("Likely affordable", "green"), 1: ("Possible, some risk", "amber"), 0: ("Unlikely", "red")}


def weekly_cost(amount: float, frequency: str) -> float:
    if frequency == "Weekly":
        return amount
    if frequency == "Fortnightly":
        return amount / 2
    return amount * 12 / 52


def simulate(net, balance, n_sims=config.N_SIMS, block=config.BLOCK_WEEKS,
             blocks_per_year=config.BLOCKS_PER_YEAR, seed=config.SIM_SEED):
    rng = np.random.default_rng(seed)
    starts = np.arange(len(net) - block + 1)
    passed = 0
    for _ in range(n_sims):
        s = rng.choice(starts, blocks_per_year)
        path = np.concatenate([net[i:i + block] for i in s])
        passed += (balance + np.cumsum(path)).min() >= 0
    return passed / n_sims


def check(a: metrics.Analysis, amount: float, frequency: str = "Weekly", type_: str = "Rent") -> dict:
    cost = weekly_cost(amount, frequency)
    dep = metrics.dependable(a.weekly_income)
    share = cost / dep
    delta = cost - config.CURRENT_RENT_WEEKLY if type_ == "Rent" else cost
    discretionary = np.array(data_gen.WEEKLY_DISCRETIONARY, dtype=float)
    net = a.weekly_income - a.regular_outflows_weekly - discretionary - delta
    rate = simulate(net, a.balance)

    share_p, rate_p = fmt.pct(share), fmt.pct(rate)
    passes = int(share_p["whole"] <= config.SHARE_LIMIT_PCT) + int(rate_p["whole"] >= config.SIM_PASS_PCT)
    label, colour = LABELS[passes]
    return {
        "type": type_, "amount": fmt.money(amount), "frequency": frequency,
        "weekly_cost": fmt.money(cost), "share": share_p, "sim_pass_rate": rate_p,
        "share_passed": share_p["whole"] <= config.SHARE_LIMIT_PCT,
        "sim_passed": rate_p["whole"] >= config.SIM_PASS_PCT,
        "label": label, "colour": colour,
        "summary": "both tests passed" if passes == 2 else "one test passed" if passes == 1 else "neither test passed",
    }
