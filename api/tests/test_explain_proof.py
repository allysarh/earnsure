import re
from datetime import date

from earnsure import proof
from earnsure.providers.explain import TemplateExplanationProvider


def test_health_template_numbers():
    e = TemplateExplanationProvider().health_explanation(
        {"status": "Watch", "dependable": "$790", "regular": "$318", "buffer": "3.7", "next_status_threshold": 4})
    text = e["headline"] + " " + e["body"]
    assert e["headline"] == "Your income covers your costs. Your savings are a bit thin."
    for s in ("$790", "$318", "3.7"):
        assert s in text
    assert set(re.findall(r"\d+(?:\.\d+)?", text)) <= {"790", "318", "3.7", "4"}


def test_note_label():
    label = TemplateExplanationProvider().proof_note_label(
        "Exams, so I only took two café shifts a week and did fewer deliveries.", date(2026, 6, 8))
    assert label == "Exam period: reduced shifts (June 2026)."


def _record(**over):
    snap = {"token": "7KQ4-M2X9", "dependable": "$790", "valid_until": "2099-01-01"}
    rec = {"snapshot": snap, "signature": proof.sign(snap), "revoked": False, "valid_until": "2099-01-01"}
    rec.update(over)
    return rec


def test_tamper_detected():
    rec = _record()
    assert proof.state(rec, date(2026, 9, 29)) == "verified"
    rec["snapshot"] = dict(rec["snapshot"], dependable="$990")
    assert proof.state(rec, date(2026, 9, 29)) == "invalid"


def test_revoked_and_expired():
    assert proof.state(_record(revoked=True), date(2026, 9, 29)) == "revoked"
    assert proof.state(_record(valid_until="2026-01-01"), date(2026, 9, 29)) == "expired"


def test_token_format():
    token, statement = proof.new_token()
    assert re.fullmatch(r"[2-9A-HJKMNP-Z]{4}-[2-9A-HJKMNP-Z]{4}", token)
    assert statement == "ES-" + token.replace("-", "")
