import { ArrowUp, LoaderCircle, X } from "lucide-react";
import { useUiStore } from "../../store";

export function Loader({ label = "Chargement…" }) {
  return <div className="flex min-h-32 items-center justify-center gap-2 text-slate-500" role="status"><LoaderCircle className="h-5 w-5 animate-spin" />{label}</div>;
}

export function ErrorState({ error }) {
  return <p className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800" role="alert">{error?.message ?? "Les données ne sont pas disponibles pour le moment."}</p>;
}

export function EmptyState({ label = "Aucun contenu disponible." }) {
  return <p className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-slate-500">{label}</p>;
}

export function SectionTitle({ eyebrow, title, children }) {
  return <div className="mb-8 max-w-3xl"><p className="headline-rule mb-3 text-[11px] font-extrabold uppercase tracking-[.2em] text-haiti-red">{eyebrow}</p><h2 className="font-display text-3xl font-black tracking-tight text-haiti-ink sm:text-4xl">{title}</h2>{children && <p className="mt-3 leading-7 text-slate-600">{children}</p>}</div>;
}

export function BackToTop() {
  return <button type="button" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="fixed bottom-5 right-5 z-30 rounded-full bg-haiti-red p-3 text-white shadow-card transition hover:-translate-y-1" aria-label="Retour en haut"><ArrowUp /></button>;
}

export function ImageViewer() {
  const { activeImage, closeImage } = useUiStore();
  if (!activeImage) return null;
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 p-4" role="dialog" aria-modal="true" aria-label="Agrandissement de la photo" onClick={closeImage}><button type="button" className="absolute right-5 top-5 rounded-full bg-white/10 p-2 text-white" onClick={closeImage} aria-label="Fermer"><X /></button><img src={activeImage.image} alt={activeImage.legende || "Photo de la galerie"} onClick={(event) => event.stopPropagation()} className="max-h-[88vh] max-w-full rounded-lg object-contain" /></div>;
}

export function Toasts() {
  const toasts = useUiStore((state) => state.toasts);
  return <div className="fixed right-4 top-4 z-[60] space-y-2">{toasts.map((toast) => <div key={toast.id} className="rounded-xl bg-haiti-ink px-4 py-3 text-sm text-white shadow-card">{toast.message}</div>)}</div>;
}
