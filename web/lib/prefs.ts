"use client";

/** Small per-tab UI preferences (not figures), kept in sessionStorage. */
export type ProofPrefs = {
  rent_amount: number;
  rent_frequency: "Weekly" | "Fortnightly" | "Monthly";
  show_chart: boolean;
  include_note: boolean;
  valid_days: 7 | 14 | 30;
};

const KEY = "earnsure.proofPrefs";
export const DEFAULT_PREFS: ProofPrefs = {
  rent_amount: 230,
  rent_frequency: "Weekly",
  show_chart: false,
  include_note: true,
  valid_days: 30,
};

export function loadPrefs(): ProofPrefs {
  try {
    const raw = sessionStorage.getItem(KEY);
    return raw ? { ...DEFAULT_PREFS, ...JSON.parse(raw) } : DEFAULT_PREFS;
  } catch {
    return DEFAULT_PREFS;
  }
}

export function savePrefs(patch: Partial<ProofPrefs>) {
  const next = { ...loadPrefs(), ...patch };
  try {
    sessionStorage.setItem(KEY, JSON.stringify(next));
  } catch {}
  return next;
}

export function clearPrefs() {
  try {
    sessionStorage.removeItem(KEY);
    sessionStorage.removeItem(CONNECTION_KEY);
  } catch {}
}

// --- Result of the (simulated) bank connection, shown back on the Connect screen ---

export type Institution = { id: string; name: string; initials: string; logo?: string };
export type Connection = {
  institution: Institution;
  accounts: { account_id: string; name: string; masked_number: string; status: string; institution: string }[];
  transaction_count: number;
  period: string;
};

const CONNECTION_KEY = "earnsure.connection";

export function saveConnection(c: Connection) {
  try {
    sessionStorage.setItem(CONNECTION_KEY, JSON.stringify(c));
  } catch {}
}

export function loadConnection(): Connection | null {
  try {
    const raw = sessionStorage.getItem(CONNECTION_KEY);
    return raw ? (JSON.parse(raw) as Connection) : null;
  } catch {
    return null;
  }
}

export function clearConnection() {
  try {
    sessionStorage.removeItem(CONNECTION_KEY);
  } catch {}
}
