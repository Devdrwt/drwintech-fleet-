"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Home, Map, Route, Receipt, Bell } from "lucide-react";
import { useAuthStore } from "@/lib/auth/store";
import { RegisterSW } from "@/components/pwa/RegisterSW";

const TABS = [
  { href: "/client", label: "Accueil", icon: Home },
  { href: "/client/carte", label: "Carte", icon: Map },
  { href: "/client/trajets", label: "Trajets", icon: Route },
  { href: "/client/factures", label: "Factures", icon: Receipt },
  { href: "/client/alertes", label: "Alertes", icon: Bell },
];

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (!token) router.replace("/login");
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 max-w-md mx-auto">
      <RegisterSW />
      <main className="flex-1 pb-16">{children}</main>

      <nav className="fixed bottom-0 inset-x-0 max-w-md mx-auto bg-white border-t flex">
        {TABS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex-1 flex flex-col items-center py-2 text-xs ${
                active ? "text-primary" : "text-gray-500"
              }`}
            >
              <Icon size={20} />
              <span className="mt-0.5">{label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
