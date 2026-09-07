import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { list, remove, retrieve, save } from "../api/resources";
export const useList = (resource, params = {}, options = {}) => useQuery({ queryKey: [resource, params], queryFn: () => list(resource, params), ...options });
export const useDetail = (resource, id) => useQuery({ queryKey: [resource, id], queryFn: () => retrieve(resource, id), enabled: Boolean(id) });
export const useResourceMutations = (resource) => { const client = useQueryClient(); const refresh = () => client.invalidateQueries({ queryKey: [resource] }); return { save: useMutation({ mutationFn: ({ values, id }) => save(resource, values, id), onSuccess: refresh }), remove: useMutation({ mutationFn: (id) => remove(resource, id), onSuccess: refresh }) }; };
