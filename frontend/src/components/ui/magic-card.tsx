"use client";

import { useCallback, useRef, useState } from "react";
import { cn } from "@/lib/utils";

/** Carte avec halo lumineux qui suit le curseur (style MagicUI spotlight). */
export function MagicCard({
  children,
  className,
  gradientColor = "rgba(99,102,241,0.14)",
}: {
  children: React.ReactNode;
  className?: string;
  gradientColor?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: -200, y: -200 });
  const [opacity, setOpacity] = useState(0);

  const onMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const r = ref.current?.getBoundingClientRect();
    if (!r) return;
    setPos({ x: e.clientX - r.left, y: e.clientY - r.top });
  }, []);

  return (
    <div
      ref={ref}
      onMouseMove={onMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-card transition-shadow duration-300 hover:shadow-card-hover",
        className,
      )}
    >
      <div
        className="pointer-events-none absolute -inset-px rounded-2xl transition-opacity duration-300"
        style={{
          opacity,
          background: `radial-gradient(420px circle at ${pos.x}px ${pos.y}px, ${gradientColor}, transparent 40%)`,
        }}
      />
      <div className="relative">{children}</div>
    </div>
  );
}
