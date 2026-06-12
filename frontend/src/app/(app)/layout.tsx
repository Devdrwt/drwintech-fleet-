"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "motion/react";
import {
  LayoutDashboard,
  Map,
  Users,
  Cpu,
  Satellite,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/lib/auth/store";
import { cn } from "@/lib/utils";

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
      typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    if (!token) router.replace("/login");
  }, [router]);

  const initials = (user?.email ?? "?").slice(0, 2).toUpperCase();

  return (
    <div className="flex min-h-screen bg-[var(--background)]">
      {/* Sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-slate-200/70 bg-white/80 backdrop-blur-xl md:flex">
        <div className="flex h-16 items-center gap-3 px-5">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 shadow-glow">
            <Satellite className="h-5 w-5 text-white" />
          </div>
          <div className="leading-tight">
            <div className="text-sm font-semibold tracking-tight">
              Drwintech <span className="text-gradient">Fleet</span>
            </div>
            <div className="text-[11px] text-slate-400">Flotte GPS</div>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                  active ? "text-brand-700" : "text-slate-500 hover:text-slate-900",
                )}
              >
                {active && (
                  <motion.span
                    layoutId="nav-active"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    className="absolute inset-0 rounded-xl bg-brand-50 ring-1 ring-brand-100"
                  />
                )}
                <Icon
                  className={cn(
                    "relative z-10 h-[18px] w-[18px] transition-transform group-hover:scale-110",
                    active && "text-brand-600",
                  )}
                />
                <span className="relative z-10">{label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-slate-200/70 p-3">
          <div className="flex items-center gap-3 rounded-xl px-3 py-2">
            <div className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-brand-500 to-violet-600 text-xs font-semibold text-white">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-xs font-medium text-slate-700">
                {user?.email ?? "Utilisateur"}
              </div>
              <div className="text-[11px] text-slate-400">Administrateur</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Contenu */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200/70 bg-white/70 px-5 backdrop-blur-xl">
          <span className="text-sm text-slate-400">
            Plateforme de gestion de flotte GPS
          </span>
          <button
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-slate-500 transition-colors hover:bg-red-50 hover:text-red-600"
          >
            <LogOut className="h-4 w-4" />
            Déconnexion
          </button>
        </header>

        <motion.main
          key={pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="flex-1"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}
