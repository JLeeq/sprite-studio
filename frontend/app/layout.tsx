import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sprite Studio – Hybrid UI",
  description:
    "Landing experience for the Sprite generator. Gradio continues to power creation workflows while this Next.js surface handles portfolio screens."
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[var(--enhanced-bg)]">{children}</body>
    </html>
  );
}

