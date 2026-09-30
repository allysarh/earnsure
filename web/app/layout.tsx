import type { Metadata, Viewport } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-jakarta",
});

export const metadata: Metadata = {
  title: "EarnSure",
  description: "Turn irregular income into one verified page a landlord can trust.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#ffffff",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={jakarta.variable}>
      <body>
        {/* 390px phone frame on desktop, full width on phones */}
        <main className="relative mx-auto min-h-dvh w-full max-w-[390px] bg-white sm:shadow-card">{children}</main>
      </body>
    </html>
  );
}
