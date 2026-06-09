"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Cpu, Bell } from "lucide-react";
import { fleetApi, geofencingApi } from "@/lib/api/endpoints";
import { useAuthStore } from "@/lib/auth/store";

export default function ClientHome() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const units = useQuery({
    queryKey: ["client", "units"],
    queryFn: () => fleetApi.units().then((r) => r.data),
  });
  const alerts = useQuery({
    queryKey: ["client", "alerts"],
    queryFn: () => geofencingApi.alerts().then((r) => r.data),
  });

  const unitCount = units.data?.results?.length ?? units.data?.count ?? 0;
  const alertCount = alerts.data?.results?.length ?? alerts.data?.length ?? 0;

  return (
    <div className="p-4 space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Mon espace</h1>
          <p className="text-sm text-gray-500">{user?.email}</p>
        </div>
        <button onClick={logout} className="text-sm text-red-600">
          Déconnexion
        </button>
      </header>

      <div className="grid grid-cols-2 gap-3">
        <Link href="/client/carte" className="bg-white rounded-xl shadow p-4">
          <Cpu className="text-primary" />
          <div className="text-2xl font-semibold mt-2">{unitCount}</div>
          <div className="text-sm text-gray-500">Mes balises</div>
        </Link>
        <Link href="/client/alertes" className="bg-white rounded-xl shadow p-4">
          <Bell className="text-amber-500" />
          <div className="text-2xl font-semibold mt-2">{alertCount}</div>
          <div className="text-sm text-gray-500">Alertes</div>
        </Link>
      </div>

      <Link
        href="/client/carte"
        className="block bg-primary text-white text-center rounded-xl py-3 font-medium"
      >
        Voir ma flotte en temps réel
      </Link>
    </div>
  );
}
