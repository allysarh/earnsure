"""Proof snapshot, HMAC signature and tokens (TD §9.3)."""

import hashlib
import hmac
import json
import os
import secrets
from datetime import date

from . import config

SNAPSHOT_FIELDS = {
    "statement_no", "token", "applicant_display", "data_source", "period", "issued",
    "valid_until", "confidence", "rent_weekly", "share", "sim_pass_rate", "label",
    "label_colour", "dependable", "typical_left", "rent_paid_weeks", "buffer_weeks",
    "note_label", "weekly_series",
}


def _secret() -> bytes:
    s = os.environ.get("PROOF_SIGNING_SECRET")
    if not s:
        if os.environ.get("VERCEL_ENV") == "production":
            raise RuntimeError("PROOF_SIGNING_SECRET is not set")
        s = "dev-only-insecure-secret"
    return s.encode()


def canonical_json(snapshot: dict) -> str:
    return json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sign(snapshot: dict) -> str:
    return hmac.new(_secret(), canonical_json(snapshot).encode(), hashlib.sha256).hexdigest()


def verify(snapshot: dict, signature: str) -> bool:
    return hmac.compare_digest(sign(snapshot), signature)


def new_token() -> tuple[str, str]:
    """(token, statement_no), e.g. ('7KQ4-M2X9', 'ES-7KQ4M2X9')."""
    chars = "".join(secrets.choice(config.TOKEN_ALPHABET) for _ in range(8))
    return f"{chars[:4]}-{chars[4:]}", f"ES-{chars}"


def state(record: dict, today: date) -> str:
    if not verify(record["snapshot"], record["signature"]):
        return "invalid"
    if record["revoked"]:
        return "revoked"
    if today > date.fromisoformat(str(record["valid_until"])):
        return "expired"
    return "verified"


def build_snapshot(**fields) -> dict:
    snap = {k: v for k, v in fields.items() if v is not None}
    unknown = set(snap) - SNAPSHOT_FIELDS
    assert not unknown, f"fields not allowed on a proof: {unknown}"
    return snap
