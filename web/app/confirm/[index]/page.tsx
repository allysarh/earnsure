"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, useApi, type Confirmations } from "@/lib/api";
import { Button, Card, ErrorBox, IconCircle, Loading, Screen, TopBar } from "@/components/ui";

const DEFAULT_CHOICE = "one_off_personal";

// What each answer does to the figures (see LABEL_OPTIONS in api/earnsure/config.py)
const EXPLANATIONS: Record<string, string> = {
  work_income: "Payments for work count as income, and every figure will be recalculated.",
  family_support:
    "Regular family support counts as income, and every figure will be recalculated. Your proof page includes it in your totals but never shows it as a separate item.",
  one_off_personal:
    "One-off personal payments aren't counted as income. If it was for work, choose the first option and attach an invoice or message as evidence.",
  other_in: "Payments marked as something else aren't counted as income. Add a note so you remember what it was.",
};

function ConfirmForm({ data, index }: { data: Confirmations; index: number }) {
  const router = useRouter();
  const item = data.items[index];
  const [choice, setChoice] = useState(item.label ?? DEFAULT_CHOICE);
  const [note, setNote] = useState(item.note ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const total = data.items.length;
  const next = index + 1 < total ? `/confirm/${index + 1}` : "/home";

  async function save() {
    setBusy(true);
    setError(null);
    try {
      await api(`/confirmations/${item.txn_id}`, { method: "POST", body: { category: choice, note: note.trim() || null } });
      router.push(next);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save");
      setBusy(false);
    }
  }

  return (
    <>
      <div className="flex h-2 rounded-full bg-track" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={index + 1}>
        <div className="rounded-full bg-primary" style={{ width: `${((index + 1) / total) * 100}%` }} />
      </div>
      <h1 className="m-0 text-[30px] leading-[1.12]">We couldn&apos;t tell what this payment is</h1>

      <Card className="flex items-center gap-3.5 p-4">
        <IconCircle size={52} className="bg-lavender text-[16px] font-semibold text-primary-dark">{item.initials}</IconCircle>
        <div className="flex min-w-0 grow flex-col gap-0.5">
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-[15px] font-medium">{item.description}</span>
            <span className="text-[20px] font-semibold tracking-[-0.02em] text-green">{item.amount.display}</span>
          </div>
          <div className="text-[13px] leading-[1.4] text-muted">{item.detail}</div>
        </div>
      </Card>

      <fieldset className="m-0 flex flex-col gap-2 border-0 p-0">
        <legend className="mb-2 p-0 text-[17px] font-medium tracking-[-0.01em]">What was this payment?</legend>
        {data.options.map((o) => {
          const on = choice === o.category;
          return (
            <label key={o.category}
              className={`flex min-h-14 cursor-pointer items-center gap-3 rounded-full border-[1.5px] px-5 text-[15px] ${
                on ? "border-[#C6A9F2] bg-violet-soft font-medium" : "border-soft bg-soft"}`}>
              <input type="radio" name="kind" checked={on} onChange={() => setChoice(o.category)} className="m-0 h-5 w-5 accent-primary" />
              {o.label}
            </label>
          );
        })}
      </fieldset>

      <div className="flex flex-col gap-2">
        <label htmlFor="note" className="text-[14px] font-medium text-muted">Add a note (optional)</label>
        <textarea id="note" rows={2} value={note} onChange={(e) => setNote(e.target.value)} maxLength={500}
          placeholder="e.g. cousin paying back a flight"
          className="resize-none rounded-[22px] border border-field-line bg-field px-[18px] py-3.5 text-[15px]" />
      </div>
      <p className="m-0 text-[13px] leading-normal text-muted" aria-live="polite">
        {EXPLANATIONS[choice] ?? EXPLANATIONS[DEFAULT_CHOICE]}
      </p>

      {error && <ErrorBox message={error} />}
      <div className="grow" />
      <div className="flex gap-2.5">
        <Button variant="secondary" className="grow" onClick={() => router.push(next)} disabled={busy}>Skip</Button>
        <Button className="grow-[2]" onClick={save} disabled={busy}>{busy ? "Saving…" : index + 1 < total ? "Save and next" : "Save and finish"}</Button>
      </div>
    </>
  );
}

export default function Confirm() {
  const { index } = useParams<{ index: string }>();
  const i = Number(index) || 0;
  const { data, error, reload } = useApi<Confirmations>("/confirmations");
  const total = data?.items.length ?? 3;

  return (
    <Screen>
      <TopBar title={`Item ${Math.min(i + 1, total)} of ${total}`} back={i > 0 ? `/confirm/${i - 1}` : "/found"} />
      {error && <ErrorBox message={error} onRetry={reload} />}
      {!data && !error && <Loading />}
      {data && data.items[i] && <ConfirmForm key={data.items[i].txn_id} data={data} index={i} />}
      {data && !data.items[i] && <p className="text-muted">Nothing left to check.</p>}
    </Screen>
  );
}
