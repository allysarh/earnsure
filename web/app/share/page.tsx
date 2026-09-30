"use client";

import { useState } from "react";
import Link from "next/link";
import { QRCodeSVG } from "qrcode.react";
import { api, shareUrl, useApi, type CurrentProof } from "@/lib/api";
import { Button, ButtonLink, ErrorBox, Loading, Screen, Tile, TopBar } from "@/components/ui";

export default function Share() {
  const { data: p, error, reload } = useApi<CurrentProof>("/proofs/current");
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);
  const url = p ? shareUrl(p.token, p.url) : "";

  async function copy() {
    try {
      await navigator.clipboard.writeText(url);
    } catch {
      window.prompt("Copy this link", url);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function switchOff() {
    if (!p || !window.confirm("Switch off this link? Anyone who opens it will see that it has been switched off.")) return;
    setBusy(true);
    try {
      await api(`/proofs/${p.token}/revoke`, { method: "POST" });
      reload();
    } finally {
      setBusy(false);
    }
  }

  return (
    <Screen>
      <TopBar title="Proof page" back="/proof" />
      <h1 className="m-0 text-[32px] leading-[1.1]">Share with the landlord</h1>
      {error && (
        <>
          <ErrorBox message={error === "No proof yet" ? "You haven't created a share link yet." : error} onRetry={reload} />
          <ButtonLink href="/proof">Go to proof settings</ButtonLink>
        </>
      )}
      {!p && !error && <Loading />}
      {p && (
        <>
          <div className="flex flex-col items-center gap-3.5 rounded-card border border-hair bg-white px-[18px] pb-[18px] pt-[22px] shadow-card">
            <div className={`rounded-tile border border-[#ECECF0] bg-white p-3 ${p.revoked ? "opacity-25" : ""}`}>
              <QRCodeSVG value={url} size={176} fgColor="#111117" level="M" marginSize={0} title="QR code for the share link" />
            </div>
            <span className="text-[12px] text-muted">
              {p.revoked ? "This link is switched off" : "Scan to open the verified statement"}
            </span>
            <div className="flex w-full items-center gap-2 rounded-full bg-soft py-1.5 pl-[18px] pr-1.5">
              <span className="grow truncate text-[13px] font-medium">{url.replace(/^https?:\/\//, "")}</span>
              <button type="button" onClick={copy}
                className="min-h-11 min-w-[76px] cursor-pointer rounded-full border-0 bg-ink text-[14px] font-medium text-white">
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2.5">
            <Tile className="flex flex-col gap-0.5 p-3.5">
              <span className="text-[12px] font-medium text-muted">Valid until</span>
              <span className="text-[17px] font-semibold tracking-[-0.02em]">{p.valid_until}</span>
            </Tile>
            <Tile className="flex flex-col gap-0.5 p-3.5">
              <span className="text-[12px] font-medium text-muted">Opened</span>
              <span className="text-[17px] font-semibold tracking-[-0.02em]">{p.opened.text}</span>
              {p.opened.last && <span className="text-[12px] text-muted">{p.opened.last}</span>}
            </Tile>
          </div>
          <div className="flex min-h-[52px] items-center justify-between rounded-full border border-[#ECECF0] px-[18px] text-[14px]">
            <span className="text-muted">Answers</span>
            <span className="font-medium">{p.answers}</span>
          </div>
          <button type="button" onClick={reload} className="self-center text-[13px] font-medium text-primary">
            Refresh opened count
          </button>

          <div className="grow" />
          <Link href={`/p/${p.token}`} target="_blank"
            className="flex min-h-14 items-center justify-center rounded-full bg-primary text-[17px] font-medium tracking-[-0.01em] text-white no-underline shadow-cta">
            See what they&apos;ll see
          </Link>
          {!p.revoked && <Button variant="danger" onClick={switchOff} disabled={busy}>Switch off this link</Button>}
        </>
      )}
    </Screen>
  );
}
