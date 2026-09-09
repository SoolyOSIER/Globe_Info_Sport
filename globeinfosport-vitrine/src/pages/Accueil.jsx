import { useEffect, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ArrowRight, ArrowUpRight, CalendarDays, Camera, CheckCircle2, Globe2, Mail, Radio, Shield, Trophy, Users } from "lucide-react";
import { Link } from "react-router-dom";
import { Loader } from "../components/common/UI";
import { Reveal, StoryCard, formatDate, nationalCategorySlugs } from "../components/common/Editorial";
import { SEO } from "../components/common/SEO";
import { usePublicQuery } from "../hooks/publicHooks";
import { api } from "../services/api";
import "../styles/home.css";

const refresh = { refetchOnMount: "always", refetchInterval: 30_000 };
const topics = [
  { title: "Les Grenadiers", label: "La passion nationale", to: "/actualites", Icon: Users },
  { title: "Championnat", label: "Au cœur des clubs", to: "/championnat", Icon: Trophy },
  { title: "Nos expatriés", label: "Haïti sans frontières", to: "/expatries", Icon: Globe2 },
  { title: "En images", label: "L’émotion du terrain", to: "/galerie", Icon: Camera },
];
const filters = [["all", "Tout le football"], ["national", "Football national"], ["international", "International"]];
const dateTime = { dateStyle: "medium", timeStyle: "short" };

function Heading({ eyebrow, title, description, to, link = "Tout découvrir" }) {
  return <div className="home-section-heading"><div><p className="home-kicker">{eyebrow}</p><h2>{title}</h2>{description && <p className="home-description">{description}</p>}</div>{to && <Link className="home-text-link" to={to}>{link}<ArrowUpRight size={17} /></Link>}</div>;
}

function QueryContent({ query, empty, children }) {
  if (query.isLoading) return <Loader />;
  if (query.isError) return <div className="home-empty" role="alert"><p>Cette rubrique est momentanément indisponible.</p><button type="button" onClick={() => query.refetch()} className="home-text-link">Réessayer <ArrowRight size={15} /></button></div>;
  if (!query.data?.length) return <p className="home-empty">{empty}</p>;
  return children;
}

function Countdown({ date }) {
  const [now, setNow] = useState(Date.now);
  useEffect(() => {
    const interval = window.setInterval(() => setNow(Date.now()), 30_000);
    return () => window.clearInterval(interval);
  }, []);
  const remaining = new Date(date).getTime() - now;
  if (!Number.isFinite(remaining) || remaining <= 0) return <span className="home-match-note">Horaire à confirmer</span>;
  const values = [Math.floor(remaining / 86400000), Math.floor(remaining / 3600000) % 24, Math.floor(remaining / 60000) % 60];
  return <div className="home-countdown" aria-label="Temps avant le match">{values.map((value, index) => <div key={index}><b>{String(value).padStart(2, "0")}</b><span>{["jours", "heures", "min"][index]}</span></div>)}</div>;
}

function Team({ club, name }) {
  return <div className="home-team"><div className="home-crest">{club?.logo ? <img src={club.logo} alt="" /> : <Shield size={28} aria-hidden="true" />}</div><strong>{club?.nom || name || "Équipe à confirmer"}</strong></div>;
}

function MatchCenter({ next, live }) {
  const match = live.data?.[0] ?? next.data?.[0];
  const isLive = Boolean(live.data?.length);
  return <div className="home-match-card">
    <div className="home-match-top"><span className="home-kicker"><Radio size={14} /> {isLive ? "En direct" : "Prochain rendez-vous"}</span><Trophy size={19} /></div>
    {live.isLoading || next.isLoading ? <Loader /> : !match ? <div className="home-match-placeholder"><CalendarDays size={42} /><h2>Le prochain coup d’envoi se prépare.</h2><p>{next.isError || live.isError ? "Le calendrier est momentanément indisponible." : "Retrouvez ici la prochaine affiche dès sa programmation."}</p></div> : <>
      <p className="home-match-date">{formatDate(match.date_heure, dateTime)}</p>
      <div className="home-teams"><Team club={match.club_domicile_detail} /><span className="home-score">{isLive ? `${match.score_domicile ?? "–"} : ${match.score_exterieur ?? "–"}` : "VS"}</span><Team club={match.club_exterieur_detail} name={match.adversaire_texte} /></div>
      <div className="home-match-bottom"><span>{match.competition_detail?.nom || "Le rendez-vous du football"}<small>{isLive ? "Score actualisé toutes les 30 secondes" : "Avant le coup d’envoi"}</small></span>{!isLive && <Countdown date={match.date_heure} />}</div>
    </>}
    <Link to="/calendrier" className="home-match-link">Ouvrir le centre des matchs <ArrowRight size={17} /></Link>
  </div>;
}

function Newsletter() {
  const [email, setEmail] = useState("");
  const [honeypot, setHoneypot] = useState("");
  const subscription = useMutation({ mutationFn: (payload) => api.post("/public/newsletter/abonnement/", payload) });
  const error = subscription.error?.response?.data;
  return <section className="home-newsletter">
    <div><p className="home-kicker"><Mail size={16} /> Le rendez-vous des passionnés</p><h2>Le football haïtien.<br />Gardons le contact.</h2><p>Inscrivez-vous à la newsletter Globe Info Sport pour suivre les actualités et les rendez-vous de notre football.</p></div>
    <div>{subscription.isSuccess ? <div className="home-subscription-success" role="status"><CheckCircle2 size={28} /><h3>Bienvenue dans la communauté !</h3><p>Votre inscription à la newsletter est confirmée.</p></div> : <form onSubmit={(event) => { event.preventDefault(); subscription.mutate({ email: email.trim(), honeypot }); }}>
      <label htmlFor="home-newsletter-email">Votre adresse e-mail</label><div className="home-email-row"><input id="home-newsletter-email" name="email" type="email" autoComplete="email" placeholder="vous@exemple.com" required maxLength={254} value={email} onChange={(event) => setEmail(event.target.value)} /><button className="home-button home-button-red" disabled={subscription.isPending}>{subscription.isPending ? "Inscription…" : "Je m’inscris"}<ArrowRight size={17} /></button></div>
      <div hidden aria-hidden="true"><label>Site web<input tabIndex={-1} autoComplete="off" value={honeypot} onChange={(event) => setHoneypot(event.target.value)} /></label></div>
      {subscription.isError && <p className="home-form-error" role="alert">{error?.email?.[0] || error?.detail || "L’inscription a échoué. Veuillez réessayer."}</p>}
      <p className="home-privacy">Désabonnement à tout moment. <Link to="/confidentialite">Confidentialité et données personnelles</Link></p>
    </form>}</div>
  </section>;
}

export default function Accueil() {
  const [filter, setFilter] = useState("all");
  const editorial = usePublicQuery("home-editorial", "/articles/", { page_size: 36 }, refresh);
  const joueurs = usePublicQuery("home-joueurs", "/joueurs/", { emblematique: true, page_size: 4 });
  const next = usePublicQuery("home-next-matches", "/matchs/", { statut: "A_VENIR", page_size: 4, ordering: "date_heure" }, refresh);
  const live = usePublicQuery("home-live-matches", "/matchs/", { statut: "EN_COURS", page_size: 1 }, refresh);
  const competitions = usePublicQuery("competitions", "/competitions/", {});
  const competition = competitions.data?.find((item) => item.type === "CHAMPIONNAT_NATIONAL") ?? competitions.data?.[0];
  const ranking = usePublicQuery("home-ranking", `/classement/${competition?.id || 0}/`, {}, { enabled: Boolean(competition), refetchInterval: 60_000 });
  const gallery = usePublicQuery("home-gallery", "/galerie/", { page_size: 3 });
  const articles = editorial.data ?? [];
  const selected = articles.filter((article) => filter === "all" || (filter === "national" ? nationalCategorySlugs.has(article.categorie?.slug) : article.categorie?.slug === "international"));
  const lead = selected.find((article) => article.a_la_une) ?? selected[0];
  const rest = selected.filter((article) => article.id !== lead?.id);
  const national = articles.filter((article) => nationalCategorySlugs.has(article.categorie?.slug)).slice(0, 3);
  const international = articles.filter((article) => article.categorie?.slug === "international").slice(0, 3);

  return <div className="home-page">
    <SEO title="Le média du football haïtien" description="Toute l’actualité des Grenadiers, du championnat national et des talents haïtiens : articles, calendrier, classements et galerie." />
    <section className="home-hero"><div className="home-pitch" aria-hidden="true" /><div className="home-wrap home-hero-grid">
      <Reveal><p className="home-hero-eyebrow"><span /> Le football haïtien, ici et partout</p><h1>Un pays.<br />Une passion.<br /><em>Notre football.</em></h1><p className="home-hero-description">Des terrains d’Haïti aux plus grandes scènes du monde, vivez les histoires des Grenadiers, de nos clubs et des talents de la diaspora.</p><div className="home-actions"><a href="#actualites" className="home-button home-button-red">À la une <ArrowRight size={17} /></a><Link to="/calendrier" className="home-button home-button-outline"><CalendarDays size={17} /> Voir les matchs</Link></div><div className="home-hero-signature"><span>Informer.</span><span>Raconter.</span><span>Rassembler.</span></div></Reveal>
      <Reveal delay={0.1}><div className="home-match-caption"><span>LE CENTRE DES MATCHS</span><span>GLOBE INFO SPORT / FOOTBALL</span></div><MatchCenter next={next} live={live} /></Reveal>
    </div></section>

    <nav className="home-wrap home-topics" aria-label="Explorer le football haïtien">{topics.map(({ title, label, to, Icon }, index) => <Link key={title} to={to}><span className="home-topic-icon"><Icon size={23} /></span><span><small>0{index + 1} / {label}</small><strong>{title}</strong></span><ArrowUpRight className="home-topic-arrow" size={19} /></Link>)}</nav>
    {articles.length > 0 && <div className="home-wrap home-wire"><span><Radio size={15} /> Dernière publication</span><Link to={`/actualites/${articles[0].slug}`}>{articles[0].titre}<ArrowRight size={17} /></Link></div>}

    <section id="actualites" className="home-wrap home-section"><Heading eyebrow="Le choix de la rédaction" title="L’actualité à ne pas manquer." description="Les nouvelles, les analyses et les histoires qui font vibrer notre football." to="/actualites" link="Toutes les actualités" />
      <div className="home-filters" role="group" aria-label="Filtrer les articles">{filters.map(([value, label]) => <button key={value} type="button" aria-pressed={filter === value} onClick={() => setFilter(value)}>{label}</button>)}</div>
      <QueryContent query={editorial} empty="Nos premières histoires arrivent bientôt. Retrouvez en attendant les clubs et les rendez-vous du championnat.">
        {lead ? <><div className="home-news-grid"><Reveal><StoryCard article={lead} featured priority /></Reveal><aside className="home-news-aside"><p className="home-kicker">Le fil de l’actualité</p>{rest.slice(0, 3).map((article) => <StoryCard key={article.id} article={article} compact />)}{!rest.length && <p className="home-empty">D’autres articles viendront bientôt enrichir cette rubrique.</p>}<Link to="/actualites" className="home-text-link">Explorer le fil complet <ArrowRight size={16} /></Link></aside></div>{rest.length > 3 && <div className="home-story-grid home-more-stories">{rest.slice(3, 6).map((article) => <StoryCard key={article.id} article={article} />)}</div>}</> : <p className="home-empty">Aucun article n’est encore disponible dans cette sélection.</p>}
      </QueryContent>
    </section>

    <section className="home-national"><div className="home-wrap home-section"><div className="home-national-grid">
      <Reveal><div className="home-manifesto"><p className="home-kicker">Bleu & rouge, toujours</p><h2>Au cœur<br />du football<br /><em>haïtien.</em></h2><p>Les sélections qui nous rassemblent. Les clubs qui font vivre nos villes. Les joueurs qui portent nos couleurs.</p><Link to="/championnat" className="home-button home-button-outline">Explorer le championnat <ArrowUpRight size={18} /></Link><div className="home-manifesto-bottom"><Shield size={26} /><span>Le terrain est notre point de départ.<br /><strong>La passion, notre lien.</strong></span></div></div></Reveal>
      <div><Heading eyebrow="Focus national" title="Le pays au premier plan." /><QueryContent query={editorial} empty="Les nouvelles du football national seront bientôt à découvrir ici.">{national.length ? <div className="home-national-stories">{national.map((article) => <StoryCard key={article.id} article={article} compact />)}</div> : <p className="home-empty">Retrouvez prochainement les nouvelles des sélections et des clubs haïtiens.</p>}</QueryContent>
        <div className="home-ranking"><div className="home-ranking-title"><Trophy size={20} /><div><h3>La course au classement</h3><p>{competition ? `${competition.nom} · ${competition.saison}` : "Championnat national"}</p></div></div>
          {competitions.isLoading ? <Loader /> : competitions.isError ? <QueryContent query={competitions} /> : !competition ? <p className="home-empty">Le classement sera disponible à l’ouverture de la compétition.</p> : <QueryContent query={ranking} empty="Le classement sera disponible après les premiers résultats."><div className="home-table-scroll"><table><caption className="sr-only">Les cinq premiers clubs de {competition.nom}</caption><thead><tr><th scope="col">Rang</th><th scope="col">Club</th><th scope="col"><abbr title="Matchs joués">MJ</abbr></th><th scope="col"><abbr title="Différence de buts">Diff.</abbr></th><th scope="col">Points</th></tr></thead><tbody>{ranking.data?.slice(0, 5).map((row, index) => <tr key={row.id ?? index}><td><span className={index === 0 ? "home-rank-first" : ""}>{index + 1}</span></td><th scope="row">{row.club_detail?.nom || "Club"}</th><td>{row.matchs_joues}</td><td>{row.difference_buts > 0 ? "+" : ""}{row.difference_buts}</td><td><b>{row.points}</b></td></tr>)}</tbody></table></div></QueryContent>}<Link to="/championnat" className="home-ranking-link">Classements et statistiques <ArrowRight size={16} /></Link>
        </div>
      </div>
    </div></div></section>

    <section className="home-dark"><div className="home-wrap home-section"><div className="home-sport-grid"><div><Heading eyebrow="Agenda du football" title="Les prochains coups d’envoi." to="/calendrier" link="Tout le calendrier" /><QueryContent query={next} empty="Les prochaines affiches seront annoncées ici."><div className="home-fixtures">{next.data?.map((match) => <Link key={match.id} to="/calendrier"><span className="home-fixture-icon"><CalendarDays size={22} /></span><span><strong>{match.club_domicile_detail?.nom || "Équipe à confirmer"} <i>vs</i> {match.club_exterieur_detail?.nom ?? match.adversaire_texte ?? "Équipe à confirmer"}</strong><small>{formatDate(match.date_heure, dateTime)}</small></span><ArrowUpRight size={18} /></Link>)}</div></QueryContent></div>
      <div><Heading eyebrow="Talents haïtiens" title="Des visages. Des ambitions." to="/expatries" link="Nos expatriés" /><QueryContent query={joueurs} empty="Les portraits de nos talents seront bientôt à découvrir."><div className="home-players">{joueurs.data?.map((joueur) => <article key={joueur.id} className="home-player"><div>{joueur.photo ? <img src={joueur.photo} alt={joueur.nom_complet} loading="lazy" /> : <Users size={48} aria-hidden="true" />}</div><p>{joueur.poste?.nom || "Talent haïtien"}</p><h3>{joueur.nom_complet}</h3></article>)}</div></QueryContent></div></div>
      <div className="home-world"><Heading eyebrow="Haïti sans frontières" title="Nos couleurs voyagent." description="Les parcours de la diaspora et l’actualité internationale, avec le même amour du jeu." to="/expatries" link="Suivre les expatriés" /><QueryContent query={editorial} empty="Les nouvelles internationales arrivent bientôt.">{international.length ? <div className="home-story-grid">{international.map((article) => <StoryCard key={article.id} article={article} />)}</div> : <div className="home-world-note"><Globe2 size={36} /><div><h3>Le talent haïtien dépasse les frontières.</h3><p>Découvrez les parcours, les clubs et les performances de nos expatriés.</p></div><Link className="home-button home-button-outline" to="/expatries">Découvrir leurs parcours <ArrowRight size={17} /></Link></div>}</QueryContent></div>
    </div></section>

    <section className="home-wrap home-section"><Heading eyebrow="L’émotion en images" title="Le football se vit aussi du regard." description="Sur le terrain, dans les tribunes, au plus près de la passion." to="/galerie" link="Ouvrir la galerie" /><QueryContent query={gallery} empty="Notre galerie se prépare à accueillir les images du football haïtien."><div className="home-gallery">{gallery.data?.map((photo) => <Link key={photo.id} to="/galerie"><img src={photo.image} alt={photo.legende || "Football haïtien"} loading="lazy" /><span><Camera size={17} />{photo.legende || photo.album_titre || "Dans l’objectif de Globe Info Sport"}<ArrowUpRight size={18} /></span></Link>)}</div></QueryContent></section>
    <div className="home-wrap home-closing"><Reveal><Newsletter /></Reveal><div className="home-contact"><span>Une histoire, une information ou un talent à nous faire découvrir ?</span><Link to="/contact" className="home-text-link">Écrivez à la rédaction <ArrowUpRight size={17} /></Link></div></div>
  </div>;
}