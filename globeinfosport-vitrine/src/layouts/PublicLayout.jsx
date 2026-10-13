import "../styles/presentation.css";
import logo from "../assets/logo.png";
import { ArrowUpRight, Menu, PenLine, Radio, X } from "lucide-react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { useUiStore } from "../store";
import { BackToTop, ImageViewer, Toasts } from "../components/common/UI";

const links = [
  ["/", "Accueil"],
  ["/haiti", "Haïti"],
  ["/international", "International"],
  ["/championnat", "Championnats"],
  ["/calendrier", "Calendrier"],
  ["/actualites", "Actualités"],
  ["/tv", "GIS TV"],
  ["/recherche", "Recherche"],
  ["/a-propos", "À propos"],
  ["/contact", "Contact"],
];

export default function PublicLayout() {
  const open = useUiStore((state) => state.mobileMenuOpen);
  const setOpen = useUiStore((state) => state.setMobileMenuOpen);
  const redactionUrl = import.meta.env.VITE_REDACTION_URL || (import.meta.env.DEV ? `http://${window.location.hostname}:5173/` : "/redaction/");
  const nav = <nav className="flex flex-col gap-1 lg:flex-row lg:items-center lg:gap-1">{links.map(([to, label]) => <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({ isActive }) => `rounded-lg px-3 py-2 text-sm font-bold transition focus:outline-none focus:ring-2 focus:ring-white/70 ${isActive ? "bg-white/15 text-white" : "text-blue-100 hover:bg-white/10 hover:text-white"}`}>{label}</NavLink>)}<a href={redactionUrl} onClick={() => setOpen(false)} className="inline-flex items-center gap-2 rounded-lg bg-haiti-gold px-3 py-2 text-sm font-extrabold text-haiti-ink transition hover:bg-white focus:outline-none focus:ring-2 focus:ring-white/70"><PenLine className="h-4 w-4" />Espace rédaction</a></nav>;

  return <div className="min-h-screen bg-slate-50 text-slate-800">
    <a href="#contenu" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-white focus:p-4">Aller au contenu</a>
    <header className="sticky top-0 z-40 shadow-xl shadow-haiti-ink/10">
      <div className="bg-haiti-ink text-white"><div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2 text-[11px] font-bold uppercase tracking-[.13em] sm:px-6"><span className="inline-flex min-w-0 items-center gap-2 text-slate-200"><Radio className="h-3.5 w-3.5 shrink-0 text-haiti-gold" aria-hidden="true" />Tous les sports. Tous les continents.</span><a className="hidden items-center gap-1 text-haiti-gold transition hover:text-white sm:inline-flex" href="https://www.facebook.com/Globein21" target="_blank" rel="noreferrer">Facebook <ArrowUpRight className="h-3.5 w-3.5" /></a></div></div>
      <div className="border-b border-white/10 bg-haiti-blue/95 backdrop-blur"><div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6"><Link to="/" aria-label="Globe Info Sport, accueil" className="shrink-0 rounded-xl p-1 focus:outline-none focus:ring-2 focus:ring-haiti-gold"><img src={logo} alt="Globe Info Sport" width={500} height={500} className="h-16 w-16 object-contain sm:h-20 sm:w-20" /></Link><div className="hidden lg:block">{nav}</div><button type="button" className="rounded-lg p-2 text-white focus:outline-none focus:ring-2 focus:ring-white/70 lg:hidden" onClick={() => setOpen(!open)} aria-label={open ? "Fermer le menu" : "Ouvrir le menu"} aria-expanded={open}>{open ? <X /> : <Menu />}</button></div>{open && <div className="border-t border-white/10 px-4 pb-4 pt-2 lg:hidden">{nav}</div>}</div>
    </header>
    <main id="contenu"><Outlet /></main>
    <footer className="mt-16 bg-haiti-ink text-slate-200"><div className="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:px-6 md:grid-cols-[1.25fr_.85fr_.9fr]"><div><Link to="/" aria-label="Globe Info Sport, accueil" className="inline-block rounded-xl p-2 focus:outline-none focus:ring-2 focus:ring-haiti-gold"><img src={logo} alt="Globe Info Sport" width={500} height={500} className="h-32 w-32 object-contain" loading="lazy" /></Link><p className="mt-4 max-w-sm text-sm leading-6 text-slate-300">L’information sportive d’Haïti vers le monde, et du monde vers Haïti.</p><p className="mt-5 text-xs font-bold uppercase tracking-[.16em] text-haiti-gold">Informer · raconter · rassembler</p></div><div><p className="font-bold text-white">Explorer</p><div className="mt-4 grid grid-cols-2 gap-x-3 gap-y-3 text-sm">{links.slice(1).map(([to, label]) => <Link key={to} to={to} className="transition hover:text-haiti-gold">{label}</Link>)}</div></div><div><p className="font-bold text-white">Suivre Globe Info Sport</p><div className="mt-4 space-y-3 text-sm"><a href="https://www.facebook.com/Globein21" target="_blank" rel="noreferrer" className="flex items-center gap-1 transition hover:text-haiti-gold">Globe Info Sport sur Facebook <ArrowUpRight className="h-3.5 w-3.5" /></a><a href="https://www.youtube.com/@GlobeInfosports21" target="_blank" rel="noreferrer" className="flex items-center gap-1 transition hover:text-haiti-gold">Globe Info Sport sur YouTube <ArrowUpRight className="h-3.5 w-3.5" /></a><a href="mailto:redaction@globeinfosport.ht" className="block transition hover:text-haiti-gold">redaction@globeinfosport.ht</a><Link to="/mentions-legales" className="inline-block transition hover:text-haiti-gold">Mentions légales</Link></div></div></div><div className="border-t border-white/10 py-4 text-center text-xs text-slate-400">© {new Date().getFullYear()} Globe Info Sport · Tous droits réservés</div></footer>
    <BackToTop /><ImageViewer /><Toasts />
  </div>;
}
