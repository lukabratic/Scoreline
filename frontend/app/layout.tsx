import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import { LeagueSwitcher } from "@/components/LeagueSwitcher";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Scoreline",
  description: "Every NBA and Premier League game, rated.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <header className="flex items-center justify-between border-b border-border px-6 py-4">
          <Link href="/" className="text-lg font-semibold tracking-tight">
            Scoreline
          </Link>
          <LeagueSwitcher />
        </header>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
