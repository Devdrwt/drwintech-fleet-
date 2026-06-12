"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Wallet,
  Users,
  Satellite,
  BellRing,
  PackageCheck,
  Wrench,
  PauseCircle,
  TrendingUp,
} from "lucide-react";
import { reportingApi } from "@/lib/api/endpoints";
import { MagicCard } from "@/components/ui/magic-card";
import { BorderBeam } from "@/components/ui/border-beam";
import { NumberTicker } from "@/components/ui/number-ticker";
import { Stagger, StaggerItem, FadeIn } from "@/components/ui/motion";

const MONTHS_FR = [
  "janv.", "févr.", "mars", "avr.", "mai", "juin",
  "juil.", "août", "sept.", "oct.", "nov.", "déc.",
];

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => reportingApi.dashboard().then((r) => r.data),
  });
  const { data: rev } = useQuery({
    queryKey: ["revenue"],
    queryFn: () => reportingApi.revenue(12).then((r) => r.data),
  });

  const d = data ?? {};
  const series =
    rev?.series?.map((p: { month: string; total: number }) => ({
      label: MONTHS_FR[new Date(p.month).getMonth()],
      total: Number(p.total),
    })) ?? [];

  return (
    <div className="mx-auto max-w-7xl p-6 lg:p-8">
      <FadeIn>
        <p className="text-sm font-medium text-brand-600">Vue d&apos;ensemble</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">
          Tableau de <span className="text-gradient">bord</span>
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Activité de la flotte, parc et chiffre d&apos;affaires en temps réel.
        </p>
      </FadeIn>

      {isError && (
        <p className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          Erreur de chargement des indicateurs.
        </p>
      )}

      {/* KPIs */}
      <Stagger className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Kpi
          label="CA du mois"
          value={Number(d.ca_mois ?? 0)}
          suffix=" FCFA"
          icon={<Wallet className="h-5 w-5" />}
          tint="from-emerald-500 to-teal-600"
          loading={isLoading}
          beam
        />
        <Kpi
          label="Clients actifs"
          value={Number(d.clients_actifs ?? 0)}
          icon={<Users className="h-5 w-5" />}
          tint="from-brand-500 to-violet-600"
          loading={isLoading}
        />
        <Kpi
          label="Balises actives"
          value={Number(d.balises_actives ?? 0)}
          icon={<Satellite className="h-5 w-5" />}
          tint="from-sky-500 to-indigo-600"
          loading={isLoading}
        />
        <Kpi
          label="Alertes (30 j)"
          value={Number(d.alertes_30j ?? 0)}
          icon={<BellRing className="h-5 w-5" />}
          tint="from-amber-500 to-orange-600"
          loading={isLoading}
        />
      </Stagger>

      {/* Graphe CA + répartition parc */}
      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <FadeIn delay={0.1} className="lg:col-span-2">
          <div className="h-full rounded-2xl border border-slate-200/80 bg-white p-5 shadow-card">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-slate-900">
                  Chiffre d&apos;affaires
                </h2>
                <p className="text-xs text-slate-400">Encaissé, 12 derniers mois</p>
              </div>
              <span className="flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-600">
                <TrendingUp className="h-3.5 w-3.5" /> Annuel{" "}
                {new Intl.NumberFormat("fr-FR").format(Number(d.ca_annee ?? 0))} FCFA
              </span>
            </div>
            <div className="mt-4 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={series} margin={{ top: 10, right: 8, left: -16, bottom: 0 }}>
                  <defs>
                    <linearGradient id="ca" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="label"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fontSize: 11, fill: "#94a3b8" }}
                  />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    width={48}
                    tick={{ fontSize: 11, fill: "#94a3b8" }}
                    tickFormatter={(v) => new Intl.NumberFormat("fr-FR", { notation: "compact" }).format(v)}
                  />
                  <Tooltip
                    formatter={(v: number) => [
                      `${new Intl.NumberFormat("fr-FR").format(v)} FCFA`,
                      "CA",
                    ]}
                    contentStyle={{
                      borderRadius: 12,
                      border: "1px solid #e2e8f0",
                      fontSize: 12,
                      boxShadow: "0 10px 30px -10px rgba(16,24,40,0.18)",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="total"
                    stroke="#6366f1"
                    strokeWidth={2.5}
                    fill="url(#ca)"
                    animationDuration={900}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </FadeIn>

        <FadeIn delay={0.18}>
          <div className="h-full rounded-2xl border border-slate-200/80 bg-white p-5 shadow-card">
            <h2 className="text-sm font-semibold text-slate-900">État du parc</h2>
            <p className="text-xs text-slate-400">
              {Number(d.balises_total ?? 0)} balises au total
            </p>
            <div className="mt-4 space-y-3">
              <ParcRow
                icon={<Satellite className="h-4 w-4" />}
                label="Actives"
                value={Number(d.balises_actives ?? 0)}
                total={Number(d.balises_total ?? 0)}
                color="bg-emerald-500"
              />
              <ParcRow
                icon={<PauseCircle className="h-4 w-4" />}
                label="Suspendues"
                value={Number(d.balises_suspendues ?? 0)}
                total={Number(d.balises_total ?? 0)}
                color="bg-amber-500"
              />
              <ParcRow
                icon={<PackageCheck className="h-4 w-4" />}
                label="En stock"
                value={Number(d.balises_en_stock ?? 0)}
                total={Number(d.balises_total ?? 0)}
                color="bg-sky-500"
              />
              <ParcRow
                icon={<Wrench className="h-4 w-4" />}
                label="En maintenance"
                value={Number(d.balises_en_maintenance ?? 0)}
                total={Number(d.balises_total ?? 0)}
                color="bg-rose-500"
              />
            </div>
          </div>
        </FadeIn>
      </div>
    </div>
  );
}

function Kpi({
  label,
  value,
  icon,
  tint,
  suffix = "",
  loading,
  beam,
}: {
  label: string;
  value: number;
  icon: React.ReactNode;
  tint: string;
  suffix?: string;
  loading?: boolean;
  beam?: boolean;
}) {
  return (
    <StaggerItem>
      <MagicCard className="p-5">
        {beam && <BorderBeam size={140} duration={8} />}
        <div className="flex items-start justify-between">
          <span className="text-sm text-slate-500">{label}</span>
          <span
            className={`grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br ${tint} text-white shadow-glow`}
          >
            {icon}
          </span>
        </div>
        <div className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">
          {loading ? (
            <span className="inline-block h-8 w-20 animate-pulse rounded bg-slate-100" />
          ) : (
            <>
              <NumberTicker value={value} />
              <span className="text-base font-medium text-slate-400">{suffix}</span>
            </>
          )}
        </div>
      </MagicCard>
    </StaggerItem>
  );
}

function ParcRow({
  icon,
  label,
  value,
  total,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  total: number;
  color: string;
}) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="flex items-center gap-2 text-slate-600">
          <span className="text-slate-400">{icon}</span>
          {label}
        </span>
        <span className="font-semibold text-slate-900">{value}</span>
      </div>
      <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full ${color} transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
