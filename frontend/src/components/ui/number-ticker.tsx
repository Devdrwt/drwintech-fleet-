"use client";

import { useEffect, useRef } from "react";
import { useInView, useMotionValue, useSpring } from "motion/react";
import { cn } from "@/lib/utils";

/** Compteur qui s'anime de 0 à `value` quand il entre dans le viewport. */
export function NumberTicker({
  value,
  decimalPlaces = 0,
  className,
}: {
  value: number;
  decimalPlaces?: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const motionValue = useMotionValue(0);
  const spring = useSpring(motionValue, { damping: 28, stiffness: 110 });
  const inView = useInView(ref, { once: true, margin: "-20px" });

  useEffect(() => {
    if (inView) motionValue.set(value);
  }, [inView, value, motionValue]);

  useEffect(() => {
    return spring.on("change", (latest) => {
      if (!ref.current) return;
      ref.current.textContent = new Intl.NumberFormat("fr-FR", {
        minimumFractionDigits: decimalPlaces,
        maximumFractionDigits: decimalPlaces,
      }).format(Number(latest.toFixed(decimalPlaces)));
    });
  }, [spring, decimalPlaces]);

  return (
    <span ref={ref} className={cn("inline-block tabular-nums", className)}>
      0
    </span>
  );
}
