import { LoaderCircle, X } from "lucide-react";
import { useUiStore } from "../../store/uiStore";
export const Loading = () => <div className="flex min-h-28 items-center justify-center gap-2 text-slate-500"><LoaderCircle className="h-5 animate-spin" />Chargement…</div>;
const errorText = (error) => {
  if (!error?.response && error?.isAxiosError) return "Impossible de joindre l'API. Vérifiez que le serveur Django est démarré, puis réessayez.";
  const data = error?.response?.data;
  if (typeof data?.detail === "string") return data.detail;
  if (data && typeof data === "object") {
    const messages = Object.entries(data).filter(([field]) => field !== "status_code").flatMap(([field, values]) => {
      const value = Array.isArray(values) ? values.join(" ") : String(values);
      return `${field} : ${value}`;
    });
    if (messages.length) return messages.join(" — ");
  }
  return error?.message || "Une erreur est survenue.";
};
export const ErrorMessage = ({ error }) => <p className="rounded-lg bg-red-50 p-4 text-sm text-red-700" role="alert">{errorText(error)}</p>;
export function Toasts() { const toasts = useUiStore((state) => state.toasts); return <div className="fixed right-4 top-4 z-50 space-y-2">{toasts.map((toast) => <div key={toast.id} className="rounded-lg bg-slate-900 px-4 py-3 text-sm text-white shadow-panel">{toast.message}</div>)}</div>; }
export function Modal({ title, onClose, children }) { return <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/45 p-4" role="dialog" aria-modal="true"><div className="max-h-[90vh] w-full max-w-2xl overflow-auto rounded-2xl bg-white p-6 shadow-panel"><div className="mb-5 flex items-center justify-between"><h2 className="font-display text-xl font-black text-haiti-ink">{title}</h2><button type="button" onClick={onClose} aria-label="Fermer"><X /></button></div>{children}</div></div>; }
