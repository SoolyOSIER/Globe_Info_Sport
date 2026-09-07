import api, { dataOf } from "./axiosClient";
export const list = async (resource, params = {}) => dataOf(await api.get(`/${resource}/`, { params }));
export const retrieve = async (resource, id) => dataOf(await api.get(`/${resource}/${id}/`));
export const save = async (resource, values, id) => { const config = values instanceof FormData ? { headers: { "Content-Type": "multipart/form-data" } } : {}; return dataOf(id ? await api.patch(`/${resource}/${id}/`, values, config) : await api.post(`/${resource}/`, values, config)); };
export const remove = (resource, id) => api.delete(`/${resource}/${id}/`);
