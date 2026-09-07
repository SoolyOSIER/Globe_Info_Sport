import { useQuery } from "@tanstack/react-query";
import { publicGet } from "../services/api";

export const usePublicQuery = (key, path, params, options = {}) => useQuery({
  queryKey: [key, params],
  queryFn: () => publicGet(path, params),
  staleTime: 60_000,
  ...options,
});

export const useLiveMatches = () => usePublicQuery("live-matches", "/matchs/", { statut: "EN_COURS" }, {
  refetchInterval: 30_000,
  refetchIntervalInBackground: true,
});
