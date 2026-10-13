import { ArrowRight, CalendarDays, FileClock, FileText, Image, Mail, Plus, Radio, Trophy } from "lucide-react";
import { Link } from "react-router-dom";
import { usePage } from "../hooks/useResources";
import { ErrorMessage, Loading } from "../components/ui/UI";
import { useAuthStore } from "../store/authStore";
import { can } from "../utils/roleHierarchy";

const statuses = { BROUILLON: "Brouillon", A_VALIDER: "À valider", PUBLIE: "Publié", ARCHIVE: "Archivé" };
const date = (value) => value && !Number.isNaN(new Date(value).getTime()) ? new Intl.DateTimeFormat("fr", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Date à préciser";
function Metric({ label, query, icon: Icon, to }) {
  return <Link to={to} className="desk-metric"><div><span>{label}</span><Icon size={20} /></div><strong>{query.isLoading ? "…" : query.isError ? "—" : query.data?.count ?? 0}</strong><small>{query.isError ? "Données indisponibles" : "Ouvrir la rubrique"}<ArrowRight size={14} /></small></Link>;
}
function QuerySection({ query, empty, children }) {
  if (query.isLoading) return <Loading />;
  if (query.isError) return <ErrorMessage error={query.error} />;
  if (!query.data?.results.length) return <p className="desk-empty">{empty}</p>;
  return children;
}
export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);
  const editor = can(user, "EDITEUR_EN_CHEF");
  const articles = usePage("articles", { ordering: "-updated_at", page_size: 5 });
  const drafts = usePage("articles", { statut: "BROUILLON", page_size: 1 });
  const pending = usePage("articles", { statut: "A_VALIDER", page_size: 1 });
  const published = usePage("articles", { statut: "PUBLIE", page_size: 1 });
  const messages = usePage("messages-contact", { traite: false, page_size: 3 }, { enabled: editor });
  const live = usePage("matchs", { statut: "EN_COURS", page_size: 1 }, { refetchInterval: 30000 });
  const next = usePage("matchs", { statut: "A_VENIR", ordering: "date_heure", page_size: 4 });
  const total = (drafts.data?.count ?? 0) + (pending.data?.count ?? 0) + (published.data?.count ?? 0);
  return <div className="desk-dashboard">
    <section className="desk-hero"><div><p className="desk-eyebrow">Globe Info Sport / La rédaction</p><h1>Le terrain inspire.<br />À vous de raconter.</h1><p>Préparez vos publications, suivez les rencontres et faites vivre le sport haïtien et international sur la vitrine.</p><Link to="/articles/nouveau" className="desk-primary"><Plus size={17} /> Nouvel article</Link></div><div className="desk-hero-note"><FileText size={32} /><strong>Votre rendez-vous éditorial</strong><span>{new Intl.DateTimeFormat("fr", { dateStyle: "full" }).format(new Date())}</span><p>Une source vérifiée, un récit clair, une image qui raconte.</p></div></section>
    {editor && <section className="rounded-2xl border border-blue-100 bg-gradient-to-r from-blue-50 to-white p-5 shadow-sm"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="text-[11px] font-extrabold uppercase tracking-[.16em] text-haiti-red">Données sportives automatiques</p><h2 className="mt-1 font-display text-xl font-black text-haiti-ink">Les cinq grands championnats sont prêts à être synchronisés.</h2><p className="mt-1 max-w-2xl text-sm leading-6 text-slate-600">Équipes, calendrier, résultats et classement alimentent ensuite automatiquement la vitrine.</p></div><Link to="/championnat/competitions" className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-haiti-blue px-4 py-2.5 text-sm font-bold text-white transition hover:bg-haiti-ink">Gérer les compétitions <ArrowRight size={16} /></Link></div></section>}
    <div className="desk-section-title"><h2>La rédaction en un regard</h2><span>Vos données actuelles</span></div>
    <div className="desk-metrics"><Metric label="Brouillons" query={drafts} icon={FileText} to="/articles" /><Metric label="Articles à valider" query={pending} icon={FileClock} to="/articles" /><Metric label="Articles publiés" query={published} icon={Trophy} to="/articles" /><Metric label="Matchs en direct" query={live} icon={Radio} to="/championnat/matchs" /></div>
    <div className="desk-columns"><section className="desk-panel"><div className="desk-panel-title"><div><p className="desk-eyebrow">Le fil de la rédaction</p><h2>Derniers contenus modifiés</h2></div><Link to="/articles" aria-label="Voir tous les articles"><ArrowRight size={20} /></Link></div><QuerySection query={articles} empty="Votre première histoire commence ici. Créez un article pour préparer sa publication.">{articles.data?.results.map((article) => <Link className="desk-list-row" key={article.id} to={`/articles/${article.id}/modifier`}><span className="desk-row-icon"><FileText size={19} /></span><div><strong>{article.titre}</strong><small>{article.categorie?.nom || "Actualité"} · {date(article.updated_at)}</small></div><span className={`desk-badge ${article.statut === "PUBLIE" ? "desk-badge-blue" : ""}`}>{statuses[article.statut] || article.statut}</span></Link>)}</QuerySection></section>
    <section className="desk-panel"><div className="desk-panel-title"><div><p className="desk-eyebrow">Du brouillon au lecteur</p><h2>Suivi des publications</h2></div></div>{drafts.isError || pending.isError || published.isError ? <p className="desk-empty">Le suivi est momentanément indisponible.</p> : drafts.isLoading || pending.isLoading || published.isLoading ? <Loading /> : <div className="desk-progress-list">{[["Brouillons", drafts], ["À valider", pending], ["Publiés", published]].map(([label, query]) => <div key={label}><div><span>{label}</span><b>{query.data?.count ?? 0}</b></div><progress aria-label={label} max={Math.max(1, total)} value={query.data?.count ?? 0} /></div>)}<p>Préparez le texte et ses sources, puis faites relire le contenu avant sa publication.</p></div>}</section></div>
    <div className="desk-section-title"><h2>Votre atelier</h2><span>Accès rapides</span></div><div className="desk-shortcuts">{[["/articles", FileText, "Écrire & publier", "Articles, sources et mise à la une"], ["/championnat/matchs", CalendarDays, "Suivre les matchs", "Affiches, scores et feuilles de match"], ["/galerie", Image, "Raconter en images", "Albums, photos et légendes"]].map(([to, Icon, title, text]) => <Link to={to} key={to}><Icon size={24} /><h3>{title}</h3><p>{text}</p><ArrowRight size={18} /></Link>)}</div>
    <div className="desk-columns"><section className="desk-panel"><div className="desk-panel-title"><div><p className="desk-eyebrow">Agenda sportif</p><h2>Prochaines rencontres</h2></div><Link to="/championnat/matchs" aria-label="Gérer les matchs"><ArrowRight size={20} /></Link></div><QuerySection query={next} empty="Aucune rencontre à venir. Ajoutez les prochaines affiches dans la gestion des matchs.">{next.data?.results.map((match) => <Link className="desk-list-row" key={match.id} to="/championnat/matchs"><span className="desk-row-icon"><CalendarDays size={19} /></span><div><strong>{match.club_domicile_detail?.nom || "Domicile"} — {match.club_exterieur_detail?.nom || match.adversaire_texte || "Adversaire à préciser"}</strong><small>{date(match.date_heure)} · {match.lieu || "Lieu à préciser"}</small></div></Link>)}</QuerySection></section>
    <section className="desk-panel"><div className="desk-panel-title"><div><p className="desk-eyebrow">{editor ? "À votre attention" : "Avant de publier"}</p><h2>{editor ? "Messages à traiter" : "Les repères de la rédaction"}</h2></div><Mail size={20} /></div>{editor ? <QuerySection query={messages} empty="Aucun message en attente de traitement.">{messages.data?.results.map((message) => <Link className="desk-list-row" to="/messages-contact" key={message.id}><div><strong>{message.sujet}</strong><small>{message.nom} · {date(message.created_at)}</small></div><ArrowRight size={16} /></Link>)}</QuerySection> : <ol className="desk-checklist"><li>Vérifier les noms, dates et résultats.</li><li>Renseigner la source et la catégorie.</li><li>Relire le titre, le chapeau et le contenu.</li><li>Confier la publication à l’éditeur en chef.</li></ol>}</section></div>
  </div>;
}
