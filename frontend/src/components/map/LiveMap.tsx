"use client";

import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

/**
 * Carte temps réel (MapLibre + OpenStreetMap — voir ADR 0004).
 * S'abonne au WebSocket backend (/ws/positions/) et déplace les marqueurs.
 */
export function LiveMap() {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markers = useRef<Record<string, maplibregl.Marker>>({});

  useEffect(() => {
    if (!containerRef.current) return;

    mapRef.current = new maplibregl.Map({
      container: containerRef.current,
      style: "https://demotiles.maplibre.org/style.json", // remplacer par tuiles dédiées/auto-hébergées
      center: [2.42, 6.37], // Cotonou / Porto-Novo
      zoom: 6,
    });

    const wsUrl =
      (process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000") + "/ws/positions/";
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      const pos = JSON.parse(event.data); // { device_imei, latitude, longitude }
      const id = pos.device_imei;
      if (!mapRef.current) return;
      if (markers.current[id]) {
        markers.current[id].setLngLat([pos.longitude, pos.latitude]);
      } else {
        markers.current[id] = new maplibregl.Marker()
          .setLngLat([pos.longitude, pos.latitude])
          .addTo(mapRef.current);
      }
    };

    return () => {
      ws.close();
      mapRef.current?.remove();
    };
  }, []);

  return <div ref={containerRef} style={{ width: "100%", height: "100%" }} />;
}
