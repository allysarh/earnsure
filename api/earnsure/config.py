"""Every threshold and constant used by the formulas in TD §7 lives here."""

from datetime import date

# --- Demo profile (TD §6) -------------------------------------------------
PERIOD_START = date(2026, 3, 30)  # Monday
N_WEEKS = 26
PERIOD_END = date(2026, 9, 27)  # Sunday
TODAY = date(2026, 9, 29)  # demo "today": proof issue date, "Week of 28 Sep"
APPLICANT_DISPLAY = "Linh N."
APPLICANT_FIRST_NAME = "Linh"

ACCOUNTS = [
    {"account_id": "acc_everyday", "name": "Everyday account", "masked_number": "•• 4821", "balance": 380.0},
    {"account_id": "acc_savings", "name": "Savings account", "masked_number": "•• 0937", "balance": 800.0},
]

# --- Classification (TD §7.1) ----------------------------------------------
TRANSFER_WINDOW_DAYS = 2
REFUND_LOOKBACK_DAYS = 60
REFUND_TERMS = ("REFUND", "REVERSAL", "RETURN")

RECURRENCE_MIN_COUNT = 3
RECURRENCE_GAP_TOLERANCE_DAYS = 3
RECURRENCE_GAPS = {"Weekly": 7, "Every fortnight": 14, "Monthly": 30}
RECURRENCE_CV_INCOME = 0.35
RECURRENCE_CV_BILLS = 0.10

# Keyword map. Income rules apply to credits only; bill rules to debits only.
PAYROLL_TERMS = ("PAY", "WAGES", "SALARY")
BUSINESS_SUFFIXES = ("PTY", "LTD", "CAFE", "RESTAURANT", "HOTEL", "BAR", "STORE")
KEYWORDS_IN = {
    "gig_income": ("QUICKDROP", "RIDEMATE", "TASKHOP"),
    "freelance_income": ("INV-",),
}
KEYWORDS_OUT = {
    "rent": ("RENT",),
    "remittance": ("WISE TRANSFER", "REMITLY-STYLE", "INTL TRANSFER"),
    "utilities": ("SPARKGRID", "NBNLINK"),
    "phone": ("TELCO",),
    "bnpl": ("PAYLATER",),
    "subscription": ("STREAMFLIX", "SOUNDBOX"),
}

# Screen-5 options -> (category, counts_as_income)
LABEL_OPTIONS = {
    "work_income": ("Payment for work I did", True),
    "family_support": ("Regular family support", False),
    "one_off_personal": ("One-off gift or repayment", False),
    "other_in": ("Something else", False),
}

# --- Health (TD §7.2–7.5) ---------------------------------------------------
DEPENDABLE_PERCENTILE = 25
STABLE_BUFFER_WEEKS = 4
TIGHT_BUFFER_WEEKS = 2
HELD_BACK_DEPOSITS = 0.0

# --- Affordability (TD §7.6) -----------------------------------------------
SHARE_LIMIT_PCT = 30  # AHURI 30:40, adapted
SIM_PASS_PCT = 90
N_SIMS = 2000
BLOCK_WEEKS = 4
BLOCKS_PER_YEAR = 13
SIM_SEED = 41
CURRENT_RENT_WEEKLY = 210.0
WHAT_IF_RENTS = (250, 290)
# Decision rule: both tests compare the DISPLAY-ROUNDED whole percentages
# (half-up), so the label always agrees with the numbers the user sees.
# e.g. $250 -> pass rate 0.8950 displays as 90%, which passes the 90% test.

# --- Trends (TD §7.7, §7.9) ------------------------------------------------
LEAN_REF_WINDOW = 8
LEAN_REF_MIN_PERIODS = 4
LEAN_THRESHOLD = 0.70
RECOVERY_THRESHOLD = 0.90

# --- Safe to spend (TD §7.8) -------------------------------------------------
TOP_UP_SHARE = 0.10

# --- Static demo data (TD §6.6) -----------------------------------------------
UPCOMING_BILL = {"name": "Energy bill", "amount": 160, "due": "13 Oct"}
DEFAULT_NOTE = "Exams, so I only took two café shifts a week and did fewer deliveries."

# --- Proofs (TD §9.3) ----------------------------------------------------------
TOKEN_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"  # no 0/O, 1/I/L look-alikes
DEMO_TOKEN = "7KQ4-M2X9"
DEMO_STATEMENT_NO = "ES-7KQ4M2X9"
DEFAULT_VALID_DAYS = 30
DATA_SOURCE = "Bank data via Consumer Data Right (demo data)"
