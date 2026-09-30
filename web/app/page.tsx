"use client";

import { useEffect } from "react";
import { api } from "@/lib/api";
import { ButtonLink, Icon, IconCircle, Logo } from "@/components/ui";

const STEPS = [
  { n: 1, bg: "bg-lavender", title: "Connect your bank", body: "Securely, with your consent. Or upload a statement." },
  { n: 2, bg: "bg-mint", title: "Check what we found", body: "Fix anything we labelled wrong before we calculate." },
  { n: 3, bg: "bg-pink", title: "Share one verified page", body: "It answers “can they pay?” and nothing more." },
];

export default function Welcome() {
  // Create the demo session (and warm up the Python function) as soon as the app opens.
  useEffect(() => {
    api("/session", { method: "POST" }).catch(() => {});
  }, []);

  return (
    <div className="flex min-h-dvh flex-col gap-[26px] px-5 pb-8 pt-6">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Logo />
          <span className="text-[20px] font-semibold tracking-[-0.02em]">EarnSure</span>
        </div>
        <button type="button" aria-label="Help"
          className="flex h-[52px] w-[52px] items-center justify-center rounded-full bg-btn">
          <Icon name="help" />
        </button>
      </div>

      <div className="mt-2 flex flex-col gap-3.5">
        <h1 className="m-0 text-[40px] leading-[1.06] tracking-[-0.035em]">Financial intelligence for irregular earners</h1>
        <p className="m-0 text-[16px] leading-[1.55] text-muted">
          We turn your income activity into one verified page a landlord can trust, with no payslip needed.
        </p>
      </div>

      <div className="flex flex-col gap-4 rounded-card border border-hair bg-white p-5 shadow-card">
        <div className="text-[14px] font-medium text-muted">How it works</div>
        {STEPS.map((s) => (
          <div key={s.n} className="flex items-center gap-3.5">
            <IconCircle className={`${s.bg} text-[15px] font-semibold`}>{s.n}</IconCircle>
            <div>
              <div className="text-[16px] font-medium tracking-[-0.01em]">{s.title}</div>
              <div className="text-[14px] leading-[1.45] text-muted">{s.body}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-3 rounded-tile bg-soft py-3 pl-3 pr-4 text-[14px] leading-[1.45] text-sub">
        <IconCircle size={40} className="border border-field-line bg-white">
          <Icon name="shield" size={18} stroke="#17756B" width={1.9} />
        </IconCircle>
        <span>We never show your transactions, employers, hours or visa details.</span>
      </div>

      <div className="grow" />
      <div className="flex flex-col gap-3">
        <ButtonLink href="/consent">Get started</ButtonLink>
        <ButtonLink href="/connect" variant="secondary">I&apos;ll upload a statement instead</ButtonLink>
      </div>
    </div>
  );
}
