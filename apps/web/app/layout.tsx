import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WikiAI MVP",
  description: "A trust-centric AI-powered encyclopedia MVP."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  );
}
