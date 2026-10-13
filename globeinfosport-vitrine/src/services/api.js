import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? `http://${window.location.hostname}:8000/api/v1`,
  withCredentials: true,
  timeout: 12_000,
});

export const dataOf = (response) => response.data?.results ?? response.data;
export const publicGet = async (url, params) => dataOf(await api.get(`/public${url}`, { params }));

export const currentEditorialUser = async () => {
  const { data: session } = await api.post("/auth/token/refresh/");
  const { data: user } = await api.get("/auth/me/", {
    headers: { Authorization: `Bearer ${session.access}` },
  });
  return user;
};
