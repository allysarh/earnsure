"""Display rounding: always half-up via Decimal, never round() (TD §7)."""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal


def half_up(x: float, places: int = 0) -> Decimal:
    q = Decimal(1).scaleb(-places)
    return Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP)


def whole(x: float) -> int:
    return int(half_up(x))


def money(x: float) -> dict:
    n = whole(x)
    sign = "-" if n < 0 else ""
    return {"value": round(float(x), 4), "display": f"{sign}${abs(n):,}"}


def pct(ratio: float) -> dict:
    return {"value": round(float(ratio), 4), "display": f"{whole(ratio * 100)}%", "whole": whole(ratio * 100)}


def one_dp(x: float) -> dict:
    return {"value": round(float(x), 4), "display": f"{half_up(x, 1)}"}


def day_month(d: date) -> str:
    return f"{d.day} {d.strftime('%b')}"


def day_month_year(d: date) -> str:
    return f"{d.day} {d.strftime('%b %Y')}"
