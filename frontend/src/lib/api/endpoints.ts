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
  simCards: () => apiClient.get("/fleet/sim-cards/"),
  recharges: () => apiClient.get("/fleet/recharges/"),
};

export const telemetryApi = {
  positions: (imei: string) =>
    apiClient.get("/telemetry/positions/", { params: { imei } }),
  trips: (imei: string) =>
    apiClient.get("/telemetry/trips/", { params: { imei } }),
};

export const billingApi = {
  transactions: () => apiClient.get("/billing/transactions/"),
  charges: () => apiClient.get("/billing/charges/"),
  invoices: () => apiClient.get("/billing/invoices/"),
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
