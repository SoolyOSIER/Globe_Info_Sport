import { create } from "zustand";

export const useUiStore = create((set) => ({
  mobileMenuOpen: false,
  activeImage: null,
  toasts: [],
  setMobileMenuOpen: (mobileMenuOpen) => set({ mobileMenuOpen }),
  openImage: (activeImage) => set({ activeImage }),
  closeImage: () => set({ activeImage: null }),
  pushToast: (toast) => {
    const id = crypto.randomUUID();
    set((state) => ({ toasts: [...state.toasts, { id, ...toast }] }));
    window.setTimeout(() => set((state) => ({ toasts: state.toasts.filter((item) => item.id !== id) })), 4500);
  },
}));
