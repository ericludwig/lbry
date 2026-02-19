import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
});

// Attach auth token
api.interceptors.request.use((config) => {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const authApi = {
  loginPM: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  registerPM: (data: {
    email: string;
    password: string;
    company_name: string;
    contact_name: string;
    phone?: string;
  }) => api.post("/auth/register/property-manager", data),
};

// Properties
export const propertiesApi = {
  list: () => api.get("/properties/"),
  create: (data: object) => api.post("/properties/", data),
  update: (id: string, data: object) => api.patch(`/properties/${id}`, data),
  delete: (id: string) => api.delete(`/properties/${id}`),
};

// Residents
export const residentsApi = {
  list: (params?: { property_id?: string; status?: string }) =>
    api.get("/residents/", { params }),
  add: (data: object) => api.post("/residents/", data),
  getSummary: () => api.get("/residents/summary"),
  getMe: () => api.get("/residents/me"),
  getMyPayments: () => api.get("/residents/me/payments"),
  optOut: (reason?: string) => api.post("/residents/me/opt-out", { reason }),
  optOutViaToken: (token: string) => api.post(`/residents/opt-out/${token}`),
};

// Payments / Stripe
export const paymentsApi = {
  startStripeOnboarding: () => api.post("/payments/pm/connect/onboard"),
  getStripeStatus: () => api.get("/payments/pm/connect/status"),
  createSetupIntent: () => api.post("/payments/resident/setup-intent"),
};

// Integrations
export const integrationsApi = {
  configurePMS: (data: object) => api.post("/integrations/pms/configure", data),
  testPMS: () => api.post("/integrations/pms/test"),
  triggerSync: () => api.post("/integrations/pms/sync"),
  getStatus: () => api.get("/integrations/pms/status"),
};
