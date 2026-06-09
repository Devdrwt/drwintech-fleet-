"use client";

import { useQuery } from "@tanstack/react-query";
import { reportingApi } from "@/lib/api/endpoints";

const LABELS: Record<string, string> = {
  clients_actifs: "Clients actifs",
  balises_total: "Balises (total)",
  balises_actives: "Balises actives",
  balises_suspendues: "Balises suspendues",
  balises_en_stock: "Balises en stock",
  balises_en_maintenance: "En maintenance",
};

export default function DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => reportingApi.dashboard().then((r) => r.data),
  });

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold text-gray-900 mb-4">Tableau de bord</h1>
      {isLoading && <p className="text-gray-500">Chargement...</p>}
      {isError && <p className="text-red-600">Erreur de chargement.</p>}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(LABELS).map(([key, label]) => (
            <div key={key} className="bg-white rounded-xl shadow p-4">
              <div className="text-sm text-gray-500">{label}</div>
              <div className="text-2xl font-semibold text-gray-900 mt-1">
                {data[key] ?? 0}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
