"use client";

import { Bar, BarChart, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export type ChartWeek = { label: string; month: string; amount: number; display: string; lean: boolean };

/** Weekly income bars with the dashed dependable line (feature 14). */
export default function IncomeChart({ weeks, dependable, dependableLabel, height = 150 }: {
  weeks: ChartWeek[]; dependable: number; dependableLabel: string; height?: number;
}) {
  // One tick per month at its first week, skipping a partial first month (e.g. 30 Mar)
  const ticks = weeks.filter((w, i) => i > 0 && weeks[i - 1].month !== w.month).map((w) => w.label);
  return (
    <div style={{ height }} role="img"
      aria-label={`Bar chart of weekly income. ${weeks.filter((w) => w.lean).length} lean weeks. Dependable line at ${dependableLabel}.`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={weeks} margin={{ top: 16, right: 0, bottom: 0, left: 0 }} barCategoryGap={2}>
          <XAxis dataKey="label" ticks={ticks} tickFormatter={(l: string) => weeks.find((w) => w.label === l)?.month ?? ""}
            tickLine={false} axisLine={{ stroke: "#ECECF0" }} interval={0}
            tick={{ fontSize: 11, fill: "#6B6B76", fontWeight: 500 }} />
          <YAxis hide domain={[0, "dataMax + 50"]} />
          <Tooltip cursor={{ fill: "rgba(107,92,231,0.06)" }}
            formatter={(_v, _n, p) => [(p.payload as ChartWeek).display, "Income"]}
            contentStyle={{ borderRadius: 14, border: "1px solid #F0F0F3", fontSize: 13 }} />
          <Bar dataKey="amount" radius={[999, 999, 2, 2]} isAnimationActive={false}>
            {weeks.map((w) => <Cell key={w.label} fill={w.lean ? "#D9912B" : "#8F80F0"} />)}
          </Bar>
          <ReferenceLine y={dependable} stroke="#6B5CE7" strokeDasharray="4 3" strokeWidth={1.5} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
