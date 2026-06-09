"use client";

import { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { authApi } from "@/lib/api/endpoints";
import { useAuthStore } from "@/lib/auth/store";

/**
 * Providers globaux : React Query + amorçage de la session.
 * Au montage, si un token est présent, on récupère le profil (/users/me).
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient());
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (!token) return;
    authApi
      .me()
      .then((r) => setUser(r.data))
      .catch(() => setUser(null));
  }, [setUser]);

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
