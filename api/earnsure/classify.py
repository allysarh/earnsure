"""Rule-based classification (TD §7.1). No AI."""

import re
from collections import defaultdict
from itertools import pairwise
from statistics import median

import numpy as np

from . import config

INCOME_CATEGORIES = {"work_income", "gig_income", "freelance_income"}
BILL_CATEGORIES = ["rent", "remittance", "utilities", "phone", "bnpl", "subscription"]

STREAM_NAMES = {
    "work_income": "Café wages",
    "gig_income": "Delivery app payouts",
    "freelance_income": "Freelance design",
    "rent": "Rent",
    "remittance": "Money sent home",
    "utilities": "Energy and internet",
    "phone": "Phone",
    "bnpl": "Buy now, pay later",
    "subscription": "Subscriptions",
}
STREAM_TAGS = {"work_income": "Work income", "gig_income": "Gig platform", "freelance_income": "Freelance"}


def _tokens(text: str) -> set[str]:
    return set(re.split(r"[^A-Z0-9&-]+", text.upper()))


def _keyword_category(txn: dict) -> str | None:
    text = f"{txn['description']} {txn['counterparty']}".upper()
    if txn["amount"] > 0:
        toks = _tokens(text)
        if toks & set(config.PAYROLL_TERMS) and toks & set(config.BUSINESS_SUFFIXES):
            return "work_income"
        for cat, words in config.KEYWORDS_IN.items():
            if any(w in text for w in words):
                return cat
    else:
        for cat, words in config.KEYWORDS_OUT.items():
            if any(w in text for w in words):
                return cat
    return None


def frequency_of(dates: list) -> tuple[str | None, float]:
    """Frequency label from the median gap between dates (±3 days of 7/14/~30)."""
    ds = sorted(dates)
    if len(ds) < 2:
        return None, 0.0
    gap = median((b - a).days for a, b in pairwise(ds))
    for label, days in config.RECURRENCE_GAPS.items():
        if abs(gap - days) <= config.RECURRENCE_GAP_TOLERANCE_DAYS:
            return label, gap
    if 20 <= gap <= 45:
        return "About monthly", gap
    return None, gap


def _cv(amounts: list[float]) -> float:
    a = np.abs(np.array(amounts))
    return float(a.std() / a.mean()) if a.mean() else 0.0


def classify(txns: list[dict]) -> list[dict]:
    out = [dict(t, direction="in" if t["amount"] > 0 else "out", category=None,
                confidence=None, source="rule", counts_as_income=False,
                stream_id=None) for t in txns]

    # Rule 1: own-account transfers (matched pairs across accounts, ±2 days)
    debits = [t for t in out if t["amount"] < 0]
    for c in (t for t in out if t["amount"] > 0):
        candidates = [d for d in debits
                      if d["category"] is None and d["account_id"] != c["account_id"]
                      and abs(d["amount"]) == c["amount"]
                      and abs((d["date"] - c["date"]).days) <= config.TRANSFER_WINDOW_DAYS]
        if candidates:
            d = min(candidates, key=lambda d: abs((d["date"] - c["date"]).days))
            for t in (c, d):
                t.update(category="own_transfer", confidence="high")

    # Rule 2: refunds
    for t in out:
        if t["category"] or t["amount"] <= 0:
            continue
        paid_before = any(d["counterparty"] == t["counterparty"]
                          and 0 <= (t["date"] - d["date"]).days <= config.REFUND_LOOKBACK_DAYS
                          for d in debits)
        if any(w in t["description"].upper() for w in config.REFUND_TERMS) or paid_before:
            t.update(category="refund", confidence="high")

    # Rule 3: keyword map
    for t in out:
        if not t["category"]:
            cat = _keyword_category(t)
            if cat:
                t.update(category=cat, confidence="high")

    # Rule 4: recurrence detection on what is left
    groups = defaultdict(list)
    for t in out:
        if not t["category"]:
            groups[(t["counterparty"], t["direction"])].append(t)
    for (_, direction), items in groups.items():
        if len(items) < config.RECURRENCE_MIN_COUNT:
            continue
        freq, _ = frequency_of([t["date"] for t in items])
        limit = config.RECURRENCE_CV_INCOME if direction == "in" else config.RECURRENCE_CV_BILLS
        if freq and _cv([t["amount"] for t in items]) < limit and direction == "in":
            for t in items:
                t.update(category="work_income", confidence="medium")

    # Rules 5 and 6: person-to-person / everything else
    for t in out:
        if not t["category"]:
            if t["direction"] == "in":
                t.update(category="unknown_in", confidence="low")
            else:
                t.update(category="discretionary", confidence="high")

    for t in out:
        t["counts_as_income"] = t["category"] in INCOME_CATEGORIES
        t["stream_id"] = t["counterparty"]
    return out


def apply_labels(classified: list[dict], labels: dict[str, str]) -> list[dict]:
    """User labels (txn_id -> category) always override the rules."""
    out = []
    for t in classified:
        if t["txn_id"] in labels:
            cat = labels[t["txn_id"]]
            t = dict(t, category=cat, source="user", confidence="high",
                     counts_as_income=config.LABEL_OPTIONS[cat][1])
        out.append(t)
    return out


def confirmation_queue(classified: list[dict]) -> list[dict]:
    """Low-confidence items, largest amount first (TD §6.4)."""
    items = [t for t in classified if t["confidence"] == "low"]
    return sorted(items, key=lambda t: -t["amount"])


def _stream(key: str, items: list[dict]) -> dict:
    """Summarise one stream. Bill streams may hold several counterparties."""
    by_cp = defaultdict(list)
    for t in items:
        by_cp[t["counterparty"]].append(t)
    typical_total, weekly_eq, freqs = 0.0, 0.0, []
    for cp_items in by_cp.values():
        freq, _ = frequency_of([t["date"] for t in cp_items])
        typical = float(np.median([abs(t["amount"]) for t in cp_items]))
        per_week = {"Weekly": 1, "Every fortnight": 0.5}.get(freq, 12 / 52)
        typical_total += typical
        weekly_eq += typical * per_week
        freqs.append(freq)
    return {"key": key, "name": STREAM_NAMES.get(key, key), "frequency": freqs[0],
            "count": len(items), "typical": typical_total, "weekly_equivalent": weekly_eq,
            "services": len(by_cp)}


def income_streams(classified: list[dict]) -> list[dict]:
    order = ["work_income", "gig_income", "freelance_income"]
    streams = []
    for cat in order:
        # Only rule-detected recurring streams, not one-off user-confirmed items
        items = [t for t in classified if t["category"] == cat and t["source"] == "rule"]
        if len(items) >= config.RECURRENCE_MIN_COUNT:
            streams.append(dict(_stream(cat, items), tag=STREAM_TAGS[cat]))
    return streams


def outgoing_streams(classified: list[dict]) -> list[dict]:
    streams = []
    for cat in BILL_CATEGORIES:
        items = [t for t in classified if t["category"] == cat]
        if items:
            streams.append(_stream(cat, items))
    return streams


def not_counted(classified: list[dict]) -> dict:
    transfers = [t for t in classified if t["category"] == "own_transfer" and t["amount"] > 0]
    refunds = [t for t in classified if t["category"] == "refund"]
    return {
        "transfers": {"count": len(transfers), "total": sum(t["amount"] for t in transfers)},
        "refunds": {"count": len(refunds), "total": sum(t["amount"] for t in refunds)},
    }
