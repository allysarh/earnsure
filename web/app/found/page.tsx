"use client";

import Link from "next/link";
import { useApi, type Streams } from "@/lib/api";
import { ButtonLink, Card, ErrorBox, Icon, IconCircle, Loading, PageTitle, Pill, Screen, SectionLabel, TopBar } from "@/components/ui";

// Front-end dummy: irregular costs aren't detected by the API yet and aren't in any figures
const IRREGULAR = [
  { name: "Textbooks and course materials", detail: "2 times · Mar and Jul", total: "$240" },
  { name: "Doctor and pharmacy", detail: "4 times · no set pattern", total: "$165" },
  { name: "Bike repair", detail: "Once · May", total: "$120" },
];

export default function Found() {
  const { data, error, reload } = useApi<Streams>("/streams");

  return (
    <Screen>
      <TopBar title="Step 3 of 3" back="/connect" />
      <PageTitle sub={data?.period}>Here&apos;s what we found</PageTitle>
      {error && <ErrorBox message={error} onRetry={reload} />}
      {!data && !error && <Loading />}
      {data && (
        <>
          {data.needs_check > 0 && (
            <Link href="/confirm/0"
              className="flex items-center gap-3 rounded-full border border-[#F1D9A8] bg-amber-bg py-2.5 pl-2.5 pr-3 text-amber no-underline">
              <IconCircle size={40} className="bg-white"><Icon name="warn" size={18} width={2} /></IconCircle>
              <span className="grow text-[14px] leading-[1.4]">
                <b className="font-semibold">{data.needs_check} {data.needs_check === 1 ? "item needs" : "items need"} your check</b>{" "}
                before we calculate anything.
              </span>
              <IconCircle size={36} className="bg-white"><Icon name="chevron" size={16} width={2} /></IconCircle>
            </Link>
          )}

          <div className="flex flex-col gap-2">
            <SectionLabel>Money coming in</SectionLabel>
            <Card className="px-4 py-1">
              {data.income.map((s, i) => (
                <div key={s.key} className={`flex min-h-[66px] items-center gap-3 ${i < data.income.length - 1 ? "border-b border-hair" : ""}`}>
                  <div className="grow">
                    <div className="text-[15px] font-medium">{s.name}</div>
                    <div className="text-[13px] text-muted">{s.detail}</div>
                  </div>
                  <div className="flex flex-col items-end gap-[3px]">
                    <div className="text-[16px] font-semibold tracking-[-0.01em]">{s.typical.display}</div>
                    <Pill tone="green" size="sm">{s.tag}</Pill>
                  </div>
                </div>
              ))}
            </Card>
          </div>

          <div className="flex flex-col gap-2">
            <SectionLabel>Money going out</SectionLabel>
            <div className="px-1 text-[13px] font-medium text-muted">Regular</div>
            <Card className="px-4 py-1">
              {data.outgoing.map((s, i) => (
                <div key={s.key} className={`flex min-h-[54px] items-center gap-3 ${i < data.outgoing.length - 1 ? "border-b border-hair" : ""}`}>
                  <div className="grow">
                    <div className="text-[15px] font-medium">{s.name}</div>
                    <div className="text-[13px] text-muted">{s.detail}</div>
                  </div>
                  <div className="text-[15px] font-semibold">{s.typical.display}</div>
                </div>
              ))}
            </Card>
            <div className="mt-1 px-1 text-[13px] font-medium text-muted">Irregular</div>
            <Card className="px-4 py-1">
              {IRREGULAR.map((s, i) => (
                <div key={s.name} className={`flex min-h-[54px] items-center gap-3 ${i < IRREGULAR.length - 1 ? "border-b border-hair" : ""}`}>
                  <div className="grow">
                    <div className="text-[15px] font-medium">{s.name}</div>
                    <div className="text-[13px] text-muted">{s.detail}</div>
                  </div>
                  <div className="flex flex-col items-end gap-[3px]">
                    <div className="text-[15px] font-semibold">{s.total}</div>
                    <Pill tone="amber" size="sm">Irregular</Pill>
                  </div>
                </div>
              ))}
            </Card>
            <div className="px-1 text-[12px] leading-[1.4] text-muted">
              Irregular totals cover the whole period and aren&apos;t counted in your regular costs.
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <SectionLabel>Not counted as income</SectionLabel>
            <div className="rounded-tile bg-soft px-4 py-1">
              <div className="flex min-h-[52px] items-center gap-3 border-b border-[#E8E8ED]">
                <div className="grow text-[15px]">
                  Transfers between your own accounts <span className="text-muted">×{data.not_counted.transfers.count}</span>
                </div>
                <div className="text-[15px] font-medium text-sub">{data.not_counted.transfers.total.display}</div>
              </div>
              <div className="flex min-h-[52px] items-center gap-3">
                <div className="grow text-[15px]">Refunds <span className="text-muted">×{data.not_counted.refunds.count}</span></div>
                <div className="text-[15px] font-medium text-sub">{data.not_counted.refunds.total.display}</div>
              </div>
            </div>
          </div>

          <div className="grow" />
          {data.needs_check > 0 ? (
            <ButtonLink href="/confirm/0">Review {data.needs_check} {data.needs_check === 1 ? "item" : "items"}</ButtonLink>
          ) : (
            <ButtonLink href="/home">See my summary</ButtonLink>
          )}
        </>
      )}
    </Screen>
  );
}
