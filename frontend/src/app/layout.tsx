import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/providers/Providers";

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
    <html lang="fr">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
