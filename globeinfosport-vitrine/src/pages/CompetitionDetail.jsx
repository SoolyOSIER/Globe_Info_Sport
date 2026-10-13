import { ArrowLeft, Building2, Trophy } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { EmptyState, ErrorState, Loader, SectionTitle } from "../components/common/UI";
import { Reveal, StoryCard } from "../components/common/Editorial";
import { SEO } from "../components/common/SEO";
import { usePublicQuery } from "../hooks/publicHooks";

const displayDate = (value) => new Intl.DateTimeFormat("fr", {
  weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
}).format(new Date(value));

const sourceLabel = (source) => source === "football-data.org" ? "Données sportives automatiques" : "Données de la rédaction";

function MatchCard({ match }) {
  const home = match.club_domicile_detail?.nom || "Domicile";
  const away = match.club_exterieur_detail?.nom || match.adversaire_texte || "Adversaire";
  const score = match.score_affichage || (match.statut === "EN_COURS" ? "En direct" : displayDate(match.date_heure));
  return <article className="rounded-2xl border border-slate-100 bg-white p-4 shadow-sm">
    <p className="mb-3 text-[10px] font-extrabold uppercase tracking-[.16em] text-slate-400">{match.statut === "TERMINE" ? "Résultat" : match.statut === "EN_COURS" ? "En direct" : "Calendrier"}</p>
    <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 text-sm font-bold text-haiti-ink">
      <span className="text-right">{home}</span><strong className="rounded-lg bg-haiti-ink px-2 py-1 text-xs text-white">{score}</strong><span>{away}</span>
    </div>
  </article>;
}

export default function CompetitionDetail() {
  const { id } = useParams();
  const competition = usePublicQuery("competition-detail", `/competitions/${id}/`, {});
  const articles = usePublicQuery("competition-articles", "/articles/", { competitions: id, page_size: 6 });
  const standings = usePublicQuery("competition-standings", `/classement/${id}/`, {});
  const matches = usePublicQuery("competition-matches", "/matchs/", { competition: id, ordering: "date_heure", page_size: 6 });

  if (competition.isLoading) return <Loader label="Chargement du championnat…" />;
  if (competition.isError) return <main className="mx-auto max-w-4xl px-4 py-12"><ErrorState error={competition.error} /></main>;

  const data = competition.data;
  const countryLabel = data.pays_detail?.nom || "International";
  const importedAt = data.derniere_synchronisation && new Intl.DateTimeFormat("fr", {
    dateStyle: "medium", timeStyle: "short",
  }).format(new Date(data.derniere_synchronisation));

  return <div className="page-texture min-h-screen">
    <SEO title={`${data.nom} ${data.saison}`} description={data.description || `Équipes, actualités et résultats de ${data.nom}.`} />
    <section className="relative overflow-hidden bg-haiti-ink text-white">
      <div className="hero-grid absolute inset-0 opacity-35" />
      <div className="absolute -right-14 top-4 h-64 w-64 rounded-full bg-haiti-red/35 blur-3xl" />
      <div className="relative mx-auto max-w-5xl px-4 py-14 sm:px-6 sm:py-20">
        <Reveal>
          <Link to="/international" className="inline-flex items-center gap-2 text-sm font-extrabold text-haiti-gold hover:text-white"><ArrowLeft className="h-4 w-4" />Retour aux championnats</Link>
          <div className="mt-9 flex flex-col gap-6 sm:flex-row sm:items-end">
            <div className="grid h-24 w-24 place-items-center overflow-hidden rounded-3xl border border-white/20 bg-white/10">{data.logo ? <img src={data.logo} alt="" className="h-full w-full object-cover" /> : <Trophy className="h-10 w-10 text-haiti-gold" />}</div>
            <div>
              <p className="text-[11px] font-extrabold uppercase tracking-[.2em] text-haiti-gold">{countryLabel}</p>
              <h1 className="mt-3 font-display text-4xl font-black sm:text-6xl">{data.nom}</h1>
              <p className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-slate-300"><span>{data.sport_detail?.nom || "Sport"}</span><span>{data.saison}</span><span>{data.clubs_detail?.length || 0} équipes</span></p>
            </div>
          </div>
        </Reveal>
      </div>
    </section>

    <main className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-16">
      <Reveal><SectionTitle eyebrow="Compétition" title="Présentation" /></Reveal>
      <Reveal>
        <div className="rounded-3xl bg-white p-7 leading-8 text-slate-600 shadow-sm">
          <p>{data.description || "La rédaction prépare la présentation complète de cette compétition."}</p>
          {data.source_donnees && <p className="mt-4 flex flex-wrap items-center gap-x-2 border-t border-slate-100 pt-4 text-xs font-bold text-slate-500"><span>{sourceLabel(data.source_donnees)}</span>{importedAt && <><span aria-hidden="true">·</span><span>Actualisées le {importedAt}</span></>}</p>}
        </div>
      </Reveal>

      <section className="mt-12 grid gap-10 lg:grid-cols-[1.1fr_.9fr]">
        <div>
          <Reveal><SectionTitle eyebrow="Tableau" title="Classement" /></Reveal>
          {standings.isLoading ? <Loader label="Chargement du classement…" /> : standings.data?.length ? <div className="overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-sm"><div className="grid grid-cols-[2.7rem_1fr_2.5rem_2.5rem] gap-2 border-b border-slate-100 bg-slate-50 px-4 py-3 text-[10px] font-extrabold uppercase tracking-[.12em] text-slate-400"><span>#</span><span>Équipe</span><span>MJ</span><span>Pts</span></div>{standings.data.map((row, index) => <div key={row.id} className="grid grid-cols-[2.7rem_1fr_2.5rem_2.5rem] gap-2 border-b border-slate-50 px-4 py-3 text-sm last:border-0"><b className="text-slate-400">{index + 1}</b><Link to={`/clubs/${row.club_detail?.slug}`} className="truncate font-bold text-haiti-ink hover:text-haiti-blue">{row.club_detail?.nom || "Équipe"}</Link><span className="text-slate-500">{row.matchs_joues}</span><b className="text-haiti-blue">{row.points}</b></div>)}</div> : <EmptyState label="Le classement apparaîtra après la première synchronisation." />}
        </div>
        <div>
          <Reveal><SectionTitle eyebrow="Matchs" title="Calendrier & résultats" /></Reveal>
          {matches.isLoading ? <Loader label="Chargement des matchs…" /> : matches.data?.length ? <div className="space-y-3">{matches.data.map((match) => <MatchCard key={match.id} match={match} />)}</div> : <EmptyState label="Le calendrier apparaîtra après la première synchronisation." />}
        </div>
      </section>

      <section className="mt-12">
        <Reveal><SectionTitle eyebrow="Équipes" title="Les clubs participants" /></Reveal>
        {data.clubs_detail?.length ? <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{data.clubs_detail.map((club) => <Reveal key={club.id}><Link to={`/clubs/${club.slug}`} className="group flex items-center gap-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-card"><div className="grid h-12 w-12 shrink-0 place-items-center overflow-hidden rounded-xl bg-slate-100 text-haiti-blue">{club.logo ? <img src={club.logo} alt="" className="h-full w-full object-cover" /> : <Building2 className="h-5 w-5" />}</div><div className="min-w-0"><h3 className="truncate font-display text-lg font-black text-haiti-ink group-hover:text-haiti-blue">{club.nom}</h3><p className="mt-1 text-sm text-slate-500">{club.ville || "Fiche club"}</p></div></Link></Reveal>)}</div> : <EmptyState label="Les équipes participantes seront ajoutées par la rédaction." />}
      </section>

      <section className="mt-14">
        <Reveal><SectionTitle eyebrow="Actualités" title={`Suivre ${data.nom}`} /></Reveal>
        {articles.isLoading ? <Loader /> : articles.data?.length ? <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">{articles.data.map((article) => <StoryCard key={article.id} article={article} />)}</div> : <EmptyState label="Aucune actualité publiée pour ce championnat." />}
      </section>
    </main>
  </div>;
}
