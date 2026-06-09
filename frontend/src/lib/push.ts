import { pushApi } from "@/lib/api/endpoints";

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const padding = "=".repeat((4 - (base64.length % 4)) % 4);
  const b64 = (base64 + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(b64);
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

/**
 * Active les notifications push : demande la permission, s'abonne au push
 * manager du service worker avec la clé VAPID, et enregistre côté backend.
 */
export async function enablePush(): Promise<string> {
  if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
    return "Notifications non supportées sur cet appareil.";
  }
  const permission = await Notification.requestPermission();
  if (permission !== "granted") return "Permission refusée.";

  const reg = await navigator.serviceWorker.ready;
  const { data } = await pushApi.vapidKey();
  if (!data.public_key) return "Clé VAPID non configurée côté serveur.";

  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(data.public_key),
  });
  await pushApi.subscribe(sub.toJSON());
  return "Notifications activées ✓";
}
