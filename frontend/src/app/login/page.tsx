"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "motion/react";
import { LogIn, Mail, Lock, Loader2, Satellite, ShieldCheck } from "lucide-react";
import { authApi } from "@/lib/api/endpoints";
import { useAuthStore } from "@/lib/auth/store";
import { AuroraBackground } from "@/components/ui/aurora-background";
import { ShimmerButton } from "@/components/ui/shimmer-button";
import { BorderBeam } from "@/components/ui/border-beam";

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
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-4 text-white">
      <AuroraBackground />

      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="relative w-full max-w-md"
      >
        <div className="glass-dark relative overflow-hidden rounded-3xl p-8 shadow-2xl">
          <BorderBeam size={220} duration={10} />

          {/* logo */}
          <motion.div
            initial={{ scale: 0.6, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.15, type: "spring", stiffness: 200, damping: 14 }}
            className="mb-6 flex items-center gap-3"
          >
            <div className="relative grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-brand-500 to-violet-600 shadow-glow">
              <Satellite className="h-6 w-6 text-white" />
              <span className="absolute inset-0 rounded-2xl ring-1 ring-white/20" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight text-white">
                Drwintech <span className="text-gradient">Fleet</span>
              </h1>
              <p className="text-xs text-white/50">Plateforme de gestion de flotte GPS</p>
            </div>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="text-2xl font-semibold tracking-tight"
          >
            Bon retour 👋
          </motion.h2>
          <p className="mt-1 text-sm text-white/50">Connectez-vous pour accéder à votre flotte.</p>

          <form onSubmit={onSubmit} className="mt-7 space-y-4">
            <Field
              icon={<Mail className="h-4 w-4" />}
              delay={0.32}
            >
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email ou téléphone"
                autoComplete="username"
                className="w-full bg-transparent py-3 pl-11 pr-4 text-sm text-white placeholder:text-white/40 outline-none"
              />
            </Field>

            <Field icon={<Lock className="h-4 w-4" />} delay={0.39}>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mot de passe"
                autoComplete="current-password"
                className="w-full bg-transparent py-3 pl-11 pr-4 text-sm text-white placeholder:text-white/40 outline-none"
              />
            </Field>

            {error && (
              <motion.p
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                className="rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-200"
              >
                {error}
              </motion.p>
            )}

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.46 }}
            >
              <ShimmerButton type="submit" disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> Connexion…
                  </>
                ) : (
                  <>
                    <LogIn className="h-4 w-4" /> Se connecter
                  </>
                )}
              </ShimmerButton>
            </motion.div>
          </form>

          <div className="mt-6 flex items-center justify-center gap-2 text-xs text-white/40">
            <ShieldCheck className="h-3.5 w-3.5" />
            Connexion chiffrée — accès réservé aux utilisateurs autorisés.
          </div>
        </div>
      </motion.div>
    </main>
  );
}

function Field({
  icon,
  children,
  delay,
}: {
  icon: React.ReactNode;
  children: React.ReactNode;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="group relative flex items-center rounded-xl border border-white/10 bg-white/5 transition-colors focus-within:border-brand-400/60 focus-within:bg-white/10"
    >
      <span className="pointer-events-none absolute left-4 text-white/40 transition-colors group-focus-within:text-brand-300">
        {icon}
      </span>
      {children}
    </motion.div>
  );
}
