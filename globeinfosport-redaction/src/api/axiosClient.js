import axios from "axios";
import { useAuthStore } from "../store/authStore";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "/api/v1", withCredentials: true, timeout: 12_000 });
api.interceptors.request.use((config) => { const token = useAuthStore.getState().accessToken; if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
let refreshing = null;
api.interceptors.response.use((response) => response, async (error) => {
  const original = error.config;
  if (error.response?.status !== 401 || original?._retried || original?.url?.includes("token/refresh")) return Promise.reject(error);
  original._retried = true;
  try { refreshing ??= api.post("/auth/token/refresh/"); const response = await refreshing; useAuthStore.getState().setSession({ user: useAuthStore.getState().user, access: response.data.access }); return api(original); } catch (refreshError) { useAuthStore.getState().clearSession(); return Promise.reject(refreshError); } finally { refreshing = null; }
});
export default api;
export const dataOf = (response) => response.data?.results ?? response.data;
