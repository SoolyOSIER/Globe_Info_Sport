import "../../desk.css";
import { useQueryClient } from "@tanstack/react-query";
import logo from "../../assets/logo.png";
import { ArrowUpRight, FileText, GalleryVerticalEnd, Globe2, LayoutDashboard, LogOut, Mail, Menu, ShieldCheck, Trophy, Users, X } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { logout } from "../../api/authApi";
import { useAuthStore } from "../../store/authStore";
import { useUiStore } from "../../store/uiStore";
import { can, roleOf } from "../../utils/roleHierarchy";
import { Toasts } from "../ui/UI";
const groups = [
  ["La rédaction", [["/", "Tableau de bord", LayoutDashboard], ["/articles", "Articles", FileText], ["/galerie", "Galerie & albums", GalleryVerticalEnd]]],
  ["Le terrain", [["/championnat/competitions", "Compétitions", Trophy], ["/championnat/clubs", "Clubs", Trophy], ["/championnat/selections", "Sélections nationales", ShieldCheck], ["/championnat/clubs/parcours", "Parcours des clubs", FileText], ["/championnat/matchs", "Matchs & résultats", Trophy], ["/joueurs", "Joueurs", Users], ["/joueurs/legendes", "Légendes", Users, "EDITEUR_EN_CHEF"], ["/expatries", "Expatriés", Globe2], ["/expatries/clubs", "Clubs des expatriés", Globe2], ["/expatries/transferts", "Transferts", Globe2]]],
  ["Le média", [["/sources-externes", "Sources externes", FileText, "EDITEUR_EN_CHEF"], ["/messages-contact", "Messages lecteurs", Mail, "EDITEUR_EN_CHEF"], ["/newsletter", "Newsletter", Mail, "EDITEUR_EN_CHEF"], ["/faq", "Questions fréquentes", FileText, "EDITEUR_EN_CHEF"], ["/vitrine", "Contenus de la vitrine", Globe2, "ADMINISTRATEUR"], ["/referentiels", "Sports, pays & rubriques", Globe2, "ADMINISTRATEUR"], ["/comptes", "Comptes & accès", ShieldCheck, "ADMINISTRATEUR"]]],
];
export default function MainLayout() {
  const client = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const clear = useAuthStore((state) => state.clearSession);
  const open = useUiStore((state) => state.sidebarOpen);
  const close = useUiStore((state) => state.closeSidebar);
  const toggle = useUiStore((state) => state.toggleSidebar);
  const navigate = useNavigate();
  const signOut = async () => { try { await logout(); } finally { await client.cancelQueries(); client.clear(); clear(); navigate("/login"); } };
  const sidebar = <aside className="desk-sidebar"><div className="desk-brand"><NavLink to="/" onClick={close} aria-label="Globe Info Sport, tableau de bord"><img src={logo} alt="" /></NavLink><div><strong>Globe Info Sport</strong><small>Espace rédaction</small></div><button className="ml-auto lg:hidden" onClick={close} aria-label="Fermer le menu"><X size={18} /></button></div><nav aria-label="Menu rédaction">{groups.map(([label, items]) => { const visible = items.filter(([, , , role]) => !role || can(user, role)); return visible.length > 0 && <div key={label}><p className="desk-nav-label">{label}</p>{visible.map(([to, title, Icon]) => <NavLink key={to} to={to} end onClick={close} className={({ isActive }) => `desk-nav-link ${isActive ? "active" : ""}`}><Icon />{title}</NavLink>)}</div>; })}</nav><div className="desk-user"><strong>{user?.prenom} {user?.nom || user?.identifiant}</strong><small>{roleOf(user)?.replaceAll("_", " ")}</small><button onClick={signOut}><LogOut size={14} />Déconnexion</button></div></aside>;
  return <div className="desk-shell"><a href="#redaction-contenu" className="sr-only focus:not-sr-only focus:fixed focus:z-50 focus:bg-white focus:p-4">Aller au contenu</a><div className="fixed inset-y-0 left-0 z-30 hidden w-64 lg:block">{sidebar}</div>{open && <div className="fixed inset-0 z-40 bg-slate-950/50 lg:hidden" onClick={close} onKeyDown={(event) => { if (event.key === "Escape") close(); }}><div onClick={(event) => event.stopPropagation()}>{sidebar}</div></div>}<div className="min-w-0 lg:pl-64"><header className="desk-topbar"><button className="lg:hidden" onClick={toggle} aria-expanded={open} aria-label="Ouvrir le menu"><Menu size={22} /></button><div><p>Votre espace de travail</p><strong>Bonjour, {user?.prenom || user?.identifiant}</strong></div><a href={import.meta.env.VITE_VITRINE_URL || "http://localhost:5174"} target="_blank" rel="noreferrer">Voir la vitrine<ArrowUpRight size={16} /></a></header><main id="redaction-contenu" className="desk-main"><Outlet /></main></div><Toasts /></div>;
}
