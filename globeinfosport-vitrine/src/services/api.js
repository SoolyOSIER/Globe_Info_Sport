import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1",
  timeout: 12_000,
});

export const dataOf = (response) => response.data?.results ?? response.data;
export const publicGet = async (url, params) => dataOf(await api.get(`/public${url}`, { params }));
