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
  } catch {}
}
