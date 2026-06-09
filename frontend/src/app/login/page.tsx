"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/lib/api/endpoints";
import { useAuthStore } from "@/lib/auth/store";

export default function LoginPage() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const setTokens = useAuthStore((s) => s.setTokens);

  const [email, setEmail] = useState("admin@drwintech.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await authApi.login(email, password);
      setTokens(data.access, data.refresh);
      if (data.user) setUser(data.user);
      router.push("/map");
    } catch {
      setError("Identifiants invalides ou serveur injoignable.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-sm bg-white p-8 rounded-xl shadow space-y-4"
      >
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Drwintech Fleet</h1>
          <p className="text-sm text-gray-500">Connexion à la plateforme</p>
        </div>

        <div className="space-y-1">
          <label className="text-sm text-gray-700">Email ou téléphone</label>
          <input
            type="text"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            autoComplete="username"
          />
        </div>

        <div className="space-y-1">
          <label className="text-sm text-gray-700">Mot de passe</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
            autoComplete="current-password"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary text-white rounded-lg py-2 text-sm font-medium disabled:opacity-60"
        >
          {loading ? "Connexion..." : "Se connecter"}
        </button>
      </form>
    </main>
  );
}
