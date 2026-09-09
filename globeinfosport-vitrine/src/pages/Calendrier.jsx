import { CalendarDays, Download, Radio, Trophy } from "lucide-react";
import { useMemo, useState } from "react";
import { EmptyState, ErrorState, Loader } from "../components/common/UI";
import { Reveal, formatDate } from "../components/common/Editorial";
import { SEO } from "../components/common/SEO";
import { useLiveMatches, usePublicQuery } from "../hooks/publicHooks";

const filters = [
  ["ALL", "Tous les matchs"],
  ["EN_COURS", "En direct"],
  ["A_VENIR", "À venir"],
  ["TERMINE", "Résultats"],
];

function statusLabel(match) {
  if (match.statut === "EN_COURS") return "En direct";
  if (match.statut === "TERMINE") return "Terminé";
  if (match.statut === "REPORTE") return "Reporté";
  return "À venir";
}

export default function Calendrier() {
  const [filter, setFilter] = useState("ALL");
  const matches = usePublicQuery("calendar", "/matchs/", { page_size: 100 }, { refetchOnMount: "always", refetchInterval: 30_000 });
  const live = useLiveMatches();
  const download = `${import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1"}/public/matchs/calendrier/telecharger/`;
  const filteredMatches = useMemo(() => (matches.data ?? []).filter((match) => filter === "ALL" || match.statut === filter), [filter, matches.data]);
  const groupedMatches = useMemo(() => filteredMatches.reduce((groups, match) => {
    const key = formatDate(match.date_heure, { weekday: "long", day: "numeric", month: "long", year: "numeric" });
    groups[key] ??= [];
    groups[key].push(match);
    return groups;
  }, {}), [filteredMatches]);

  return <div className="page-texture min-h-screen"><SEO title="Calendrier" /><section className="relative overflow-hidden bg-haiti-ink text-white"><div className="hero-grid absolute inset-0 opacity-35" /><div className="absolute -right-12 top-4 h-60 w-60 rounded-full bg-haiti-red/35 blur-3xl" /><div className="relative mx-auto flex max-w-7xl flex-wrap items-end justify-between gap-6 px-4 py-14 sm:px-6 sm:py-20"><Reveal><p className="text-[11px] font-extrabold uppercase tracking-[.22em] text-haiti-gold">Match center</p><h1 className="mt-4 max-w-3xl font-display text-4xl font-black leading-tight sm:text-6xl">Tous les rendez-vous, au même endroit.</h1><p className="mt-5 max-w-2xl leading-7 text-slate-300">Planifiez les matchs à venir, suivez le direct et retrouvez les résultats validés par la rédaction.</p></Reveal><Reveal delay={0.1}><a href={download} className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-extrabold text-haiti-blue transition hover:-translate-y-0.5 hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-white"><Download className="h-4 w-4" />Télécharger le calendrier</a></Reveal></div></section>

    <main className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">{live.data?.length > 0 && <Reveal><section className="mb-8 overflow-hidden rounded-[1.5rem] bg-haiti-red p-1 shadow-xl shadow-red-900/15"><div className="rounded-[1.35rem] border border-white/20 p-5 text-white sm:p-6"><p className="inline-flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[.16em] text-white"><Radio className="h-4 w-4 animate-pulse" />En direct maintenant</p>{live.data.map((match) => <div key={match.id} className="mt-4 grid grid-cols-[1fr_auto_1fr] items-center gap-3 text-center"><p className="font-display text-lg font-black sm:text-2xl">{match.club_domicile_detail?.nom}</p><p className="rounded-xl bg-white px-4 py-3 font-display text-2xl font-black text-haiti-red">{match.score_domicile} — {match.score_exterieur}</p><p className="font-display text-lg font-black sm:text-2xl">{match.club_exterieur_detail?.nom ?? match.adversaire_texte}</p></div>)}</div></section></Reveal>}
      <Reveal><div className="mb-9 rounded-[1.5rem] border border-slate-200 bg-white p-4 shadow-sm"><div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-haiti-blue"><Trophy className="h-5 w-5" /></div><div><p className="font-bold text-haiti-ink">Filtrer le calendrier</p><p className="text-sm text-slate-500">Les matchs en direct se rafraîchissent automatiquement.</p></div></div><div className="mt-5 flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Statut des matchs">{filters.map(([value, label]) => <button key={value} type="button" role="tab" aria-selected={filter === value} onClick={() => setFilter(value)} className={`whitespace-nowrap rounded-full px-4 py-2 text-sm font-extrabold transition focus:outline-none focus:ring-2 focus:ring-haiti-blue ${filter === value ? "bg-haiti-blue text-white" : "bg-slate-100 text-slate-600 hover:bg-blue-50 hover:text-haiti-blue"}`}>{label}</button>)}</div></div></Reveal>
      {matches.isLoading ? <Loader label="Chargement du calendrier…" /> : matches.isError ? <ErrorState error={matches.error} /> : !filteredMatches.length ? <EmptyState label="Aucun match ne correspond à ce filtre." /> : <div className="space-y-9">{Object.entries(groupedMatches).map(([day, dayMatches], groupIndex) => <section key={day}><Reveal delay={groupIndex * 0.04}><h2 className="mb-4 flex items-center gap-2 font-display text-xl font-black capitalize text-haiti-ink"><CalendarDays className="h-5 w-5 text-haiti-red" />{day}</h2></Reveal><div className="space-y-3">{dayMatches.map((match, index) => <Reveal key={match.id} delay={index * 0.04}><article className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-card sm:p-5"><div className="flex flex-wrap items-center justify-between gap-3"><p className="text-xs font-bold text-slate-500">{formatDate(match.date_heure, { hour: "2-digit", minute: "2-digit" })} · {match.competition_nom}</p><span className={`rounded-full px-3 py-1 text-[10px] font-extrabold uppercase tracking-[.12em] ${match.statut === "EN_COURS" ? "bg-red-100 text-haiti-red" : match.statut === "TERMINE" ? "bg-slate-100 text-slate-700" : "bg-blue-50 text-haiti-blue"}`}>{statusLabel(match)}</span></div><div className="mt-4 grid grid-cols-[1fr_auto_1fr] items-center gap-3 text-center"><p className="font-display text-base font-black text-haiti-ink sm:text-xl">{match.club_domicile_detail?.nom}</p><p className="min-w-14 rounded-lg bg-slate-50 px-3 py-2 font-display text-lg font-black text-haiti-ink">{match.score_affichage ?? "VS"}</p><p className="font-display text-base font-black text-haiti-ink sm:text-xl">{match.club_exterieur_detail?.nom ?? match.adversaire_texte}</p></div><p className="mt-3 text-center text-sm text-slate-500">{match.lieu || "Lieu à confirmer"}{match.diffusion_tv ? ` · ${match.diffusion_tv}` : ""}</p></article></Reveal>)}</div></section>)}</div>}</main>
  </div>;
}
