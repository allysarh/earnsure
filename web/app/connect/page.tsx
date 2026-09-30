"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useRouter } from "next/navigation";
import { Button, ButtonLink, Card, ErrorBox, Icon, IconCircle, PageTitle, Pill, Screen, Spinner, TopBar } from "@/components/ui";

type Connection = {
  accounts: { account_id: string; name: string; masked_number: string; status: string }[];
  transaction_count: number;
  period: string;
};

export default function Connect() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [banks, setBanks] = useState<string[]>([]);
  const [conn, setConn] = useState<Connection | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query.trim()) return;
    const t = setTimeout(() => {
      api<{ institutions: string[] }>(`/institutions?q=${encodeURIComponent(query)}`)
        .then((r) => setBanks(r.institutions))
        .catch(() => setBanks([]));
    }, 200);
    return () => clearTimeout(t);
  }, [query]);

  async function connect() {
    setBusy(true);
    setError(null);
    try {
      setConn(await api<Connection>("/connect", { method: "POST" }));
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) return router.replace("/");
      setError(e instanceof Error ? e.message : "Could not connect");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen>
      <TopBar title="Step 2 of 3" back="/consent" />
      <PageTitle sub="Link every account your money moves through, so we can tell transfers between them apart from real income.">
        Connect your accounts
      </PageTitle>

      <div className="flex flex-col gap-2">
        <label htmlFor="bank" className="text-[14px] font-medium text-muted">Find your bank</label>
        <input id="bank" type="search" placeholder="Search banks" value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="min-h-[52px] rounded-full border border-field-line bg-field px-5 text-[15px]" />
        {query.trim() && (
          <div className="flex flex-wrap gap-2" aria-live="polite">
            {(banks.length ? banks : ["No match. Demo banks only"]).map((b) => (
              <button key={b} type="button" onClick={connect} disabled={!banks.length || busy || !!conn}
                className="min-h-11 rounded-full border border-field-line bg-white px-4 text-[14px] font-medium disabled:opacity-60">
                {b}
              </button>
            ))}
          </div>
        )}
      </div>

      <Card className="flex flex-col px-4 py-1.5">
        {conn ? (
          conn.accounts.map((a, i) => (
            <div key={a.account_id} className="flex min-h-[68px] items-center gap-3 border-b border-hair">
              <IconCircle className={i === 0 ? "bg-lavender" : "bg-mint"}>
                <Icon name="bank" stroke={i === 0 ? "#4B3CC4" : "#17756B"} />
              </IconCircle>
              <div className="grow">
                <div className="text-[15px] font-medium">{a.name}</div>
                <div className="text-[13px] text-muted">{a.masked_number}</div>
              </div>
              <Pill tone="green">{a.status}</Pill>
            </div>
          ))
        ) : (
          <button type="button" onClick={connect} disabled={busy}
            className="flex min-h-[68px] items-center gap-3 border-b border-hair text-left text-[15px] font-medium">
            <IconCircle className="bg-lavender"><Icon name="bank" stroke="#4B3CC4" /></IconCircle>
            <span className="grow">{busy ? "Connecting securely…" : "Connect with Consumer Data Right"}</span>
            {busy && <span className="text-primary"><Spinner /></span>}
          </button>
        )}
        <div className="flex min-h-[60px] items-center gap-3 text-[15px] font-medium text-muted" aria-disabled="true">
          <IconCircle className="bg-btn"><Icon name="plus" size={18} /></IconCircle>
          Add another account
        </div>
      </Card>

      <div className="flex items-center gap-3 text-[13px] text-muted">
        <span className="h-px grow bg-[#ECECF0]" />or<span className="h-px grow bg-[#ECECF0]" />
      </div>

      {/* Placeholder (feature 2): statement upload is not built for the hackathon */}
      <div aria-disabled="true"
        className="flex items-start gap-3.5 rounded-card border-[1.5px] border-dashed border-[#CFC8F3] bg-[#FAF9FF] p-4">
        <IconCircle className="bg-pink"><Icon name="upload" /></IconCircle>
        <span className="flex flex-col gap-0.5">
          <span className="text-[15px] font-medium">Upload a statement (CSV or PDF) <Pill size="sm">Coming soon</Pill></span>
          <span className="text-[13px] leading-[1.45] text-muted">
            If your bank isn&apos;t listed. Uploaded statements are marked &ldquo;self-uploaded&rdquo; and count as lower confidence.
          </span>
        </span>
      </div>

      {error && <ErrorBox message={error} onRetry={connect} />}
      <div className="grow" />
      {conn ? (
        <>
          <div className="text-center text-[13px] text-muted">
            Fetched {conn.transaction_count} transactions · {conn.period}
          </div>
          <ButtonLink href="/found">Analyse my earnings</ButtonLink>
        </>
      ) : (
        <Button onClick={connect} disabled={busy}>{busy ? "Connecting…" : "Connect my bank"}</Button>
      )}
    </Screen>
  );
}
