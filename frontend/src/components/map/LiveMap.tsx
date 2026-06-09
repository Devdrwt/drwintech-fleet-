"use client";

import { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

interface LivePosition {
  device_imei: string;
  latitude: number;
  longitude: number;
  speed?: number;
  fixTime?: string;
}

/**
 * Carte temps réel (MapLibre + OpenStreetMap — voir ADR 0004).
 * S'abonne au WebSocket backend (/ws/positions/) et déplace les marqueurs.
 */
export function LiveMap() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markers = useRef<Record<string, maplibregl.Marker>>({});
  const [connected, setConnected] = useState(false);
  const [last, setLast] = useState<LivePosition | null>(null);
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: "https://demotiles.maplibre.org/style.json",
      center: [2.42, 6.37], // Cotonou / Porto-Novo
      zoom: 6,
    });
    mapRef.current = map;

    const wsBase = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    const ws = new WebSocket(`${wsBase}/ws/positions/`);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => {
      let pos: LivePosition;
      try {
        pos = JSON.parse(event.data);
      } catch {
        return;
      }
      if (pos.latitude == null || pos.longitude == null) return;
      const id = pos.device_imei;
      if (markers.current[id]) {
        markers.current[id].setLngLat([pos.longitude, pos.latitude]);
      } else {
        markers.current[id] = new maplibregl.Marker()
          .setLngLat([pos.longitude, pos.latitude])
          .addTo(map);
      }
      map.easeTo({ center: [pos.longitude, pos.latitude], duration: 500 });
      setLast(pos);
      setCount((c) => c + 1);
    };

    return () => {
      ws.close();
      map.remove();
    };
  }, []);

  return (
    <div className="relative w-full h-full">
      <div ref={containerRef} className="absolute inset-0" />
      <div className="absolute top-3 left-3 z-10 bg-white/90 rounded-lg shadow px-3 py-2 text-sm">
        <div className="flex items-center gap-2">
          <span
            className={`inline-block w-2 h-2 rounded-full ${
              connected ? "bg-green-500" : "bg-red-500"
            }`}
          />
          <span className="font-medium">
            {connected ? "Temps réel connecté" : "Déconnecté"}
          </span>
        </div>
        <div className="text-gray-600 mt-1">Positions reçues : {count}</div>
        {last && (
          <div className="text-gray-600">
            {last.device_imei} — {last.latitude.toFixed(4)},{" "}
            {last.longitude.toFixed(4)}
            {last.speed != null && ` — ${last.speed} km/h`}
          </div>
        )}
      </div>
    </div>
  );
}
