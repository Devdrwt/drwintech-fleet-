"use client";

import { LiveMap } from "@/components/map/LiveMap";

export default function MapPage() {
  return (
    <div className="h-[calc(100vh-3.5rem)]">
      <LiveMap />
    </div>
  );
}
