"use client";

import { LiveMap } from "@/components/map/LiveMap";

export default function ClientMapPage() {
  return (
    <div className="h-[calc(100vh-4rem)]">
      <LiveMap />
    </div>
  );
}
