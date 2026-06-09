import axios, {
  AxiosError,
  AxiosRequestConfig,
  InternalAxiosRequestConfig,
} from "axios";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  timeout: 30000,
});

const ACCESS = "access_token";
const REFRESH = "refresh_token";

// --- Intercepteur requête : ajoute le Bearer ---
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token =
    typeof window !== "undefined" ? localStorage.getItem(ACCESS) : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// --- Intercepteur réponse : refresh auto sur 401 ---
let refreshing: Promise<string> | null = null;

apiClient.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        if (!refreshing) refreshing = refreshAccessToken();
        const newToken = await refreshing;
        refreshing = null;
        original.headers = original.headers ?? {};
        (original.headers as Record<string, string>).Authorization =
          `Bearer ${newToken}`;
        return apiClient(original);
      } catch {
        clearTokens();
        if (typeof window !== "undefined") window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

async function refreshAccessToken(): Promise<string> {
  const refresh = localStorage.getItem(REFRESH);
  if (!refresh) throw new Error("no refresh token");
  const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
    refresh,
  });
  localStorage.setItem(ACCESS, data.access);
  return data.access;
}

export function clearTokens() {
  localStorage.removeItem(ACCESS);
  localStorage.removeItem(REFRESH);
}
