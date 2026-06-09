"use client";

import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { geofencingApi } from "@/lib/api/endpoints";
import { enablePush } from "@/lib/push";

interface Alert {
  id?: number;
  type: string;
  device_imei: string;
  payload: Record<string, unknown>;
  triggered_at?: string;
}

const LABEL: Record<string, string> = {
  enter: "Entrée de zone",
  exit: "Sortie de zone",
  overspeed: "Excès de vitesse",
  low_battery: "Batterie faible",
  sim_low_balance: "Crédit SIM faible",
};

export default function AlertesPage() {
  const { data } = useQuery({
    queryKey: ["client", "alerts", "list"],
    queryFn: () => geofencingApi.alerts().then((r) => r.data),
  });
  const [live, setLive] = useState<Alert[]>([]);
  const [pushMsg, setPushMsg] = useState<string | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const token =
      typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    const ws = new WebSocket(`${base}/ws/alerts/${token ? `?token=${token}` : ""}`);
    ws.onmessage = (e) => {
      try {
        setLive((prev) => [JSON.parse(e.data), ...prev]);
      } catch {
        /* ignore */
      }
    };
    return () => ws.close();
  }, []);

  const history: Alert[] = data?.results ?? data ?? [];
  const all = [...live, ...history];

  return (
    <div className="p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">Alertes</h1>
        <button
          onClick={async () => setPushMsg(await enablePush())}
          className="text-xs bg-primary text-white rounded-lg px-3 py-1.5"
        >
          Activer les notifications
        </button>
      </div>
      {pushMsg && <p className="text-xs text-gray-500">{pushMsg}</p>}
      {all.length === 0 && (
        <p className="text-gray-400 text-sm">Aucune alerte.</p>
      )}
      {all.map((a, i) => (
        <div key={a.id ?? `live-${i}`} className="bg-white rounded-xl shadow p-3">
          <div className="flex justify-between">
            <span className="font-medium text-gray-800">
              {LABEL[a.type] || a.type}
            </span>
            <span className="font-mono text-xs text-gray-500">{a.device_imei}</span>
          </div>
          <div className="text-sm text-gray-600 mt-1">
            {a.type === "overspeed"
              ? `${a.payload?.speed} km/h (seuil ${a.payload?.threshold})`
              : String(a.payload?.geofence ?? "")}
          </div>
          {a.triggered_at && (
            <div className="text-xs text-gray-400 mt-1">
              {new Date(a.triggered_at).toLocaleString("fr-FR")}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
