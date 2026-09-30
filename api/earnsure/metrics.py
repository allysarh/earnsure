"""Dependable income, cashflow, buffer and status (TD §7.2–7.5, §7.8)."""

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from . import classify, config, data_gen


@dataclass
class Analysis:
    txns: list[dict]
    weekly_income: np.ndarray
    regular_outflows_weekly: float
    balance: float


@lru_cache(maxsize=1)
def base_classified() -> tuple:
    return tuple(classify.classify(data_gen.build()))


def analyse(labels: dict[str, str] | None = None) -> Analysis:
    txns = classify.apply_labels(list(base_classified()), labels or {})
    weekly = np.zeros(config.N_WEEKS)
    for t in txns:
        if t["counts_as_income"]:
            weekly[data_gen.week_index(t["date"])] += t["amount"]
    outflows = sum(s["weekly_equivalent"] for s in classify.outgoing_streams(txns))
    balance = sum(a["balance"] for a in config.ACCOUNTS)
    return Analysis(txns, weekly, outflows, balance)


def dependable(weekly: np.ndarray) -> float:
    """Earned or exceeded in 3 of 4 weeks."""
    return float(np.percentile(weekly, config.DEPENDABLE_PERCENTILE, method="lower"))


def typical(weekly: np.ndarray) -> float:
    return float(np.median(weekly))


def cashflow(a: Analysis) -> dict:
    left = a.weekly_income - a.regular_outflows_weekly
    return {"typical_left": float(np.median(left)), "lowest_left": float(left.min())}


def buffer_weeks(a: Analysis) -> float:
    return (a.balance - config.HELD_BACK_DEPOSITS) / a.regular_outflows_weekly


def status(dep: float, outflows: float, typical_left: float, buffer: float) -> str:
    if dep >= outflows and buffer >= config.STABLE_BUFFER_WEEKS:
        return "Stable"
    if typical_left < 0 and buffer < config.TIGHT_BUFFER_WEEKS:
        return "Tight"
    return "Watch"


def safe_to_spend(dep: float, outflows: float, buffer: float) -> dict:
    top_up = config.TOP_UP_SHARE * dep if buffer < config.STABLE_BUFFER_WEEKS else 0.0
    return {"top_up": top_up, "safe": max(0.0, dep - outflows - top_up)}


def summary(a: Analysis) -> dict:
    dep = dependable(a.weekly_income)
    cf = cashflow(a)
    buf = buffer_weeks(a)
    return {
        "dependable": dep,
        "typical": typical(a.weekly_income),
        "regular_outflows": a.regular_outflows_weekly,
        "typical_left": cf["typical_left"],
        "lowest_left": cf["lowest_left"],
        "buffer_weeks": buf,
        "balance": a.balance,
        "status": status(dep, a.regular_outflows_weekly, cf["typical_left"], buf),
        **safe_to_spend(dep, a.regular_outflows_weekly, buf),
    }
