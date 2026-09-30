"""Open-banking placeholder (TD §8.1). No network calls."""

import os
import time
from typing import Protocol

from .. import config, data_gen

FICTIONAL_BANKS = [
    "Harbourline Bank", "Southern Cross Mutual", "Koala Credit Union",
    "Wattle Savings Bank", "Bluegum Bank", "Coastal People's Bank",
]


class BankDataProvider(Protocol):
    def list_institutions(self, query: str) -> list[str]: ...
    def connect(self, session_id: str, consent_days: int) -> dict: ...
    def fetch_transactions(self, session_id: str) -> list[dict]: ...


class DummyBankProvider:
    delay_seconds = 1.5

    def list_institutions(self, query: str) -> list[str]:
        q = query.strip().lower()
        return [b for b in FICTIONAL_BANKS if q in b.lower()]

    def connect(self, session_id: str, consent_days: int) -> dict:
        time.sleep(self.delay_seconds)
        txns = self.fetch_transactions(session_id)
        return {
            "accounts": [{k: a[k] for k in ("account_id", "name", "masked_number")} | {"status": "Connected"}
                         for a in config.ACCOUNTS],
            "transaction_count": len(txns),
            "period": f"{config.PERIOD_START.day} {config.PERIOD_START:%b} – "
                      f"{config.PERIOD_END.day} {config.PERIOD_END:%b %Y}",
        }

    def fetch_transactions(self, session_id: str) -> list[dict]:
        return data_gen.build()


def get_bank_provider() -> BankDataProvider:
    name = os.environ.get("BANK_PROVIDER", "dummy")
    if name != "dummy":
        raise ValueError(f"Unsupported BANK_PROVIDER: {name}")
    return DummyBankProvider()
