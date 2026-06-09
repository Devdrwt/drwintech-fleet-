"use client";

import { useQuery } from "@tanstack/react-query";
import { telemetryApi } from "@/lib/api/endpoints";

interface Trip {
  id: number;
  device_imei: string;
  start_time: string;
  end_time: string;
  distance_km: number;
  duration_s: number;
  max_speed: number;
}

export default function TrajetsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["client", "trips"],
    queryFn: () => telemetryApi.allTrips().then((r) => r.data),
  });
  const trips: Trip[] = data?.results ?? data ?? [];

  return (
    <div className="p-4 space-y-3">
      <h1 className="text-lg font-semibold text-gray-900">Trajets</h1>
      {isLoading && <p className="text-gray-500">Chargement...</p>}
      {!isLoading && trips.length === 0 && (
        <p className="text-gray-400 text-sm">Aucun trajet enregistré.</p>
      )}
      {trips.map((t) => (
        <div key={t.id} className="bg-white rounded-xl shadow p-3 text-sm">
          <div className="flex justify-between">
            <span className="font-mono text-gray-700">{t.device_imei}</span>
            <span className="text-gray-500">
              {new Date(t.start_time).toLocaleString("fr-FR")}
            </span>
          </div>
          <div className="text-gray-600 mt-1">
            {t.distance_km?.toFixed(1)} km · {Math.round((t.duration_s || 0) / 60)} min ·
            max {t.max_speed} km/h
          </div>
        </div>
      ))}
    </div>
  );
}
