import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });

export const metadata: Metadata = {
  title: "Drwintech Fleet",
  description: "Plateforme indépendante de gestion de flotte GPS",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, title: "Fleet Client", statusBarStyle: "black-translucent" },
};

export const viewport = {
  themeColor: "#4f46e5",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={inter.variable}>
      <body className="font-sans">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
