import api, { dataOf } from "./axiosClient";
export const list = async (resource, params = {}) => {
  const items = [];
  let page = 1;
  while (true) {
    const { data } = await api.get(`/${resource}/`, { params: { ...params, page, page_size: 100 } });
    if (Array.isArray(data)) return data;
    items.push(...data.results);
    if (!data.next) return items;
    page += 1;
  }
};
export const listPage = async (resource, params = {}) => {
  const { data } = await api.get(`/${resource}/`, { params });
  return Array.isArray(data) ? { results: data, count: data.length, next: null, previous: null } : data;
};
export const retrieve = async (resource, id) => dataOf(await api.get(`/${resource}/${id}/`));
export const save = async (resource, values, id) => { const config = values instanceof FormData ? { headers: { "Content-Type": "multipart/form-data" } } : {}; return dataOf(id ? await api.patch(`/${resource}/${id}/`, values, config) : await api.post(`/${resource}/`, values, config)); };
export const remove = (resource, id) => api.delete(`/${resource}/${id}/`);
