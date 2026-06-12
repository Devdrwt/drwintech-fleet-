"use client";

import { cn } from "@/lib/utils";

/** Fond animé : dégradés "aurora" flottants + grille + masque radial. */
export function AuroraBackground({ className }: { className?: string }) {
  return (
    <div className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}>
      {/* base sombre */}
      <div className="absolute inset-0 bg-[#070a1a]" />

      {/* halos colorés flottants */}
      <div className="absolute -left-32 -top-32 h-[36rem] w-[36rem] rounded-full bg-brand-600/40 blur-[120px] animate-float" />
      <div
        className="absolute -right-24 top-1/4 h-[30rem] w-[30rem] rounded-full bg-violet-500/40 blur-[120px] animate-float"
        style={{ animationDelay: "-2s" }}
      />
      <div
        className="absolute bottom-[-10rem] left-1/3 h-[34rem] w-[34rem] rounded-full bg-fuchsia-500/30 blur-[130px] animate-float"
        style={{ animationDelay: "-4s" }}
      />

      {/* grille subtile */}
      <div className="absolute inset-0 bg-grid opacity-[0.18] mask-radial" />

      {/* vignettage */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_30%,#070a1a_95%)]" />
    </div>
  );
}
