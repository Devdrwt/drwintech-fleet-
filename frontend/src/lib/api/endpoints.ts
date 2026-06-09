import { apiClient } from "./client";

// Regroupe les appels API par domaine (miroir des apps backend).
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post("/auth/token/", { email, password }),
  me: () => apiClient.get("/users/me/"),
};

export const clientsApi = {
  list: (params?: Record<string, unknown>) =>
    apiClient.get("/clients/", { params }),
  get: (id: number) => apiClient.get(`/clients/${id}/`),
  get360: (id: number) => apiClient.get(`/clients/${id}/360/`),
  create: (payload: unknown) => apiClient.post("/clients/", payload),
};

export const fleetApi = {
  units: (params?: Record<string, unknown>) =>
    apiClient.get("/fleet/units/", { params }),
  unit: (id: number) => apiClient.get(`/fleet/units/${id}/`),
  createUnit: (payload: unknown) => apiClient.post("/fleet/units/", payload),
  simCards: () => apiClient.get("/fleet/sim-cards/"),
  recharges: () => apiClient.get("/fleet/recharges/"),
};

export const telemetryApi = {
  positions: (imei: string) =>
    apiClient.get("/telemetry/positions/", { params: { imei } }),
  trips: (imei: string) =>
    apiClient.get("/telemetry/trips/", { params: { imei } }),
  allTrips: () => apiClient.get("/telemetry/trips/"),
};

export const geofencingApi = {
  alerts: () => apiClient.get("/geofencing/alerts/"),
};

export const pushApi = {
  vapidKey: () => apiClient.get("/push/vapid-public-key/"),
  subscribe: (sub: unknown) => apiClient.post("/push/subscribe/", sub),
};

export const billingApi = {
  transactions: () => apiClient.get("/billing/transactions/"),
  charges: () => apiClient.get("/billing/charges/"),
  invoices: () => apiClient.get("/billing/invoices/"),
  // Initie un paiement pour une facture (provider = fedapay/gobipay/notchpay).
  pay: (invoiceId: number, provider = "fedapay") =>
    apiClient.post("/billing/pay/", { invoice: invoiceId, provider }),
};

export const maintenanceApi = {
  interventions: () => apiClient.get("/maintenance/interventions/"),
};

export const reportingApi = {
  dashboard: () => apiClient.get("/reporting/dashboard/"),
};

export const integrationsApi = {
  traccarStatus: () => apiClient.get("/integrations/traccar/status/"),
};
