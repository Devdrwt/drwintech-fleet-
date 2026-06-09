"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth/store";

/**
 * Layout protégé : redirige vers /login si aucun token.
 * (Contrôle d'affichage ; l'autorisation réelle reste côté backend.)
 */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
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
    <div className="min-h-screen flex flex-col">
      <header className="h-14 border-b bg-white flex items-center justify-between px-4">
        <span className="font-semibold text-gray-900">Drwintech Fleet</span>
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
      <div className="flex-1">{children}</div>
    </div>
  );
}
