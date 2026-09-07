import api from "./axiosClient";
export const login = (payload) => api.post("/auth/login/", payload).then((response) => response.data);
export const logout = () => api.post("/auth/logout/");
export const currentUser = () => api.get("/auth/me/").then((response) => response.data);
export const restoreSession = async () => {
  const { data } = await api.post("/auth/token/refresh/");
  const user = (await api.get("/auth/me/", {
    headers: { Authorization: `Bearer ${data.access}` },
  })).data;
  return { user, access: data.access };
};
