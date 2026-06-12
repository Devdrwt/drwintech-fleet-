"use client";

import { ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

/** Bouton avec halo brillant qui balaie la surface au survol (style MagicUI). */
export const ShimmerButton = forwardRef<
  HTMLButtonElement,
  ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, children, ...props }, ref) => {
  return (
    <button
      ref={ref}
      className={cn(
        "group relative inline-flex items-center justify-center overflow-hidden rounded-xl px-6 py-3 font-medium text-white transition-all duration-300",
        "bg-gradient-to-r from-brand-600 to-violet-600 shadow-glow",
        "hover:shadow-[0_0_50px_-5px_rgba(99,102,241,0.6)] active:scale-[0.98]",
        "disabled:cursor-not-allowed disabled:opacity-60 disabled:shadow-none",
        className,
      )}
      {...props}
    >
      {/* reflet brillant */}
      <span className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/30 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </button>
  );
});
ShimmerButton.displayName = "ShimmerButton";
