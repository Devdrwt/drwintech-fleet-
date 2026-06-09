"use client";

import { useEffect } from "react";

/** Enregistre le service worker de la PWA (espace client). */
export function RegisterSW() {
  useEffect(() => {
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        /* enregistrement best-effort */
      });
    }
  }, []);
  return null;
}
