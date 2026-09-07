import { create } from "zustand";

export const useAuthStore = create((set) => ({
  user: null,
  accessToken: null,
  hydrated: false,
  setSession: ({ user, access }) => set((state) => ({
    user,
    accessToken: access === undefined ? state.accessToken : access,
    hydrated: true,
  })),
  setHydrated: () => set({ hydrated: true }),
  clearSession: () => set({ user: null, accessToken: null, hydrated: true }),
}));
