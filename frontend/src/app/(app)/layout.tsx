"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, Map, Users, Cpu } from "lucide-react";
import { useAuthStore } from "@/lib/auth/store";

const NAV = [
  { href: "/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/map", label: "Carte temps réel", icon: Map },
  { href: "/clients", label: "Clients", icon: Users },
  { href: "/materiel", label: "Matériel", icon: Cpu },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (!token) router.replace("/login");
  }, [router]);

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 bg-gray-900 text-gray-100 flex flex-col">
        <div className="h-14 flex items-center px-4 font-semibold border-b border-gray-800">
          Drwintech Fleet
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm ${
                  active ? "bg-primary text-white" : "hover:bg-gray-800"
                }`}
              >
                <Icon size={18} />
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="flex-1 flex flex-col">
        <header className="h-14 border-b bg-white flex items-center justify-between px-4">
          <span className="text-sm text-gray-500">Plateforme de gestion de flotte GPS</span>
          <div className="flex items-center gap-3 text-sm text-gray-600">
            {user && <span>{user.email}</span>}
            <button
              onClick={() => {
                logout();
                router.replace("/login");
              }}
              className="text-red-600 hover:underline"
            >
              Déconnexion
            </button>
          </div>
        </header>
        <main className="flex-1 bg-gray-50">{children}</main>
      </div>
    </div>
  );
}
