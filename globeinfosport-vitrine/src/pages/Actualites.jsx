import { ArrowRight, ArrowUpRight, Goal, Search, SlidersHorizontal, Sparkles, Trophy } from "lucide-react";
import { useMemo, useState } from "react";
import { EmptyState, ErrorState, Loader } from "../components/common/UI";
import { Reveal, StoryCard } from "../components/common/Editorial";
import { SEO } from "../components/common/SEO";
import { usePublicQuery } from "../hooks/publicHooks";

const requestOptions = { refetchOnMount: "always", refetchInterval: 30_000 };

export default function Actualites() {
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");
  const [sortOrder, setSortOrder] = useState("recent");
  const articles = usePublicQuery("articles", "/articles/", { search, page_size: 100 }, requestOptions);
  const categories = usePublicQuery("public-categories", "/categories/", {});
  const chiffres = usePublicQuery("chiffres", "/chiffres-cles/", {});
  const filExterne = usePublicQuery("fil-externe", "/fil-externe/", { page_size: 6 }, { refetchInterval: 60_000 });
  const filteredArticles = useMemo(() => {
    const filtered = (articles.data ?? []).filter((article) => activeCategory === "all" || article.categorie?.slug === activeCategory);
    return filtered.sort((left, right) => {
      const leftDate = new Date(left.date_publication ?? 0).getTime();
      const rightDate = new Date(right.date_publication ?? 0).getTime();
      return sortOrder === "older" ? leftDate - rightDate : rightDate - leftDate;
    });
  }, [activeCategory, articles.data, sortOrder]);
  const headline = filteredArticles.find((article) => article.a_la_une) ?? filteredArticles[0];
  const secondaryStories = filteredArticles.filter((article) => article.id !== headline?.id).slice(0, 2);
  const remainingStories = filteredArticles.filter((article) => article.id !== headline?.id && !secondaryStories.some((story) => story.id === article.id));

  return <div className="page-texture min-h-screen">
    <SEO title="Actualités football" description="Les dernières actualités du football haïtien et international : sélections, clubs, résultats et grands rendez-vous." />

    <section className="relative isolate overflow-hidden bg-haiti-ink text-white">
      <div className="hero-grid absolute inset-0 -z-10 opacity-35" />
      <div className="absolute -right-20 -top-28 -z-10 h-96 w-96 rounded-full bg-haiti-red/30 blur-3xl" />
      <div className="absolute -bottom-40 left-1/3 -z-10 h-80 w-80 rounded-full bg-haiti-blue/50 blur-3xl" />
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:px-6 sm:py-20 lg:grid-cols-[1fr_auto] lg:items-end">
        <Reveal>
          <p className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-[11px] font-extrabold uppercase tracking-[.2em] text-haiti-gold"><Goal className="h-4 w-4" /> Globe Info Sport · Football</p>
          <h1 className="mt-5 max-w-3xl font-display text-4xl font-black leading-[1.04] tracking-tight sm:text-6xl">Le football, <span className="text-haiti-gold">au cœur</span> de l’actualité.</h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300 sm:text-lg">Les Grenadiers, les clubs haïtiens et les grandes scènes du monde : les histoires qui font vibrer le jeu, racontées par notre rédaction.</p>
          <a href="#actualites-recentes" className="mt-8 inline-flex items-center gap-2 rounded-xl bg-haiti-red px-5 py-3 text-sm font-extrabold text-white shadow-lg shadow-black/15 transition hover:-translate-y-0.5 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-white">Explorer les actualités <ArrowRight className="h-4 w-4" /></a>
        </Reveal>
        <Reveal delay={0.08}>
          <div className="hidden min-w-52 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm sm:block">
            <p className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-[.15em] text-slate-300"><Sparkles className="h-4 w-4 text-haiti-gold" /> Le regard de la rédaction</p>
            <p className="mt-3 font-display text-xl font-black">Du terrain à votre écran.</p>
            <p className="mt-2 text-sm leading-6 text-slate-400">Analyses, résultats et récits, au plus près du football.</p>
          </div>
        </Reveal>
      </div>
    </section>

    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 sm:py-14">
      {chiffres.data?.length > 0 && <Reveal><section className="mb-12 grid grid-cols-2 gap-3 lg:grid-cols-4" aria-label="Le sport en chiffres">{chiffres.data.map((item) => <article key={item.id} className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm"><p className="font-display text-3xl font-black text-haiti-blue">{item.valeur}</p><p className="mt-1 text-sm font-medium text-slate-500">{item.libelle}</p></article>)}</section></Reveal>}

      {categories.data?.length > 0 && <section className="mb-14" aria-labelledby="explorer-rubriques"><Reveal><div className="mb-5 flex items-end justify-between gap-3"><div><p className="text-[11px] font-extrabold uppercase tracking-[.2em] text-haiti-red">Explorez le terrain</p><h2 id="explorer-rubriques" className="mt-2 font-display text-2xl font-black tracking-tight text-haiti-ink sm:text-3xl">Choisir une rubrique</h2></div><span className="hidden text-sm font-medium text-slate-500 sm:inline">Les sujets qui font l’actualité</span></div></Reveal><div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">{categories.data.map((category, index) => {
        const count = (articles.data ?? []).filter((article) => article.categorie?.slug === category.slug).length;
        const selected = activeCategory === category.slug;
        return <Reveal key={category.id} delay={(index % 4) * 0.04}><button type="button" aria-pressed={selected} onClick={() => { setActiveCategory(selected ? "all" : category.slug); document.getElementById("actualites-recentes")?.scrollIntoView({ behavior: "smooth", block: "start" }); }} className={`group w-full rounded-2xl border p-4 text-left transition hover:-translate-y-0.5 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-haiti-blue sm:p-5 ${selected ? "border-haiti-blue bg-haiti-blue text-white shadow-lg shadow-haiti-blue/15" : "border-slate-200 bg-white text-haiti-ink hover:border-blue-200"}`}><span className={`grid h-10 w-10 place-items-center rounded-xl ${selected ? "bg-white/15 text-haiti-gold" : "bg-blue-50 text-haiti-blue group-hover:bg-haiti-blue group-hover:text-white"}`}><Goal className="h-5 w-5" /></span><span className="mt-4 block truncate font-display font-black">{category.nom}</span><span className={`mt-1 block text-xs ${selected ? "text-blue-100" : "text-slate-500"}`}>{count} {count === 1 ? "article" : "articles"}</span></button></Reveal>;
      })}</div></section>}

      <section aria-labelledby="a-la-une">
        <Reveal><div className="mb-5 flex flex-wrap items-end justify-between gap-3"><div><p className="flex items-center gap-2 text-[11px] font-extrabold uppercase tracking-[.2em] text-haiti-red"><span className="h-1.5 w-1.5 rounded-full bg-haiti-red" /> Sélection de la rédaction</p><h2 id="a-la-une" className="mt-2 font-display text-2xl font-black tracking-tight text-haiti-ink sm:text-3xl">À la une</h2></div><span className="rounded-full bg-white px-3 py-1.5 text-xs font-bold text-slate-500 shadow-sm">Les histoires du moment</span></div></Reveal>
        {articles.isLoading ? <div className="rounded-3xl border border-slate-200 bg-white p-10"><Loader label="Chargement des actualités…" /></div> : articles.isError ? <ErrorState error={articles.error} /> : headline ? <div className="grid gap-4 lg:grid-cols-[1.55fr_.8fr]">
          <Reveal><StoryCard article={headline} featured priority /></Reveal>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">{secondaryStories.map((article, index) => <Reveal key={article.id} delay={index * 0.06}><StoryCard article={article} compact /></Reveal>)}{secondaryStories.length === 0 && <div className="flex min-h-36 items-center rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-sm leading-6 text-slate-500">Les prochaines histoires de la rédaction apparaîtront ici.</div>}</div>
        </div> : <div className="rounded-3xl border border-slate-200 bg-white p-8"><EmptyState label="Aucun article n’est encore publié dans cette rubrique." /></div>}
      </section>

      <section id="actualites-recentes" className="scroll-mt-28 pt-14" aria-labelledby="actualites-titre">
        <Reveal><div className="flex flex-col gap-5 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between"><div><p className="text-[11px] font-extrabold uppercase tracking-[.2em] text-haiti-red">Le fil du football</p><h2 id="actualites-titre" className="mt-2 font-display text-2xl font-black tracking-tight text-haiti-ink sm:text-3xl">Dernières actualités</h2><p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">Retrouvez les nouvelles des clubs, des sélections et des compétitions.</p></div>
          <div className="grid w-full gap-3 sm:grid-cols-[1fr_auto] lg:max-w-2xl"><label className="relative block"><Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Équipe, compétition, sujet…" aria-label="Rechercher une actualité" className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm outline-none transition placeholder:text-slate-400 focus:border-haiti-blue focus:ring-4 focus:ring-blue-100" /></label><label className="sr-only" htmlFor="actualites-tri">Trier les actualités</label><select id="actualites-tri" value={sortOrder} onChange={(event) => setSortOrder(event.target.value)} className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-600 outline-none focus:border-haiti-blue focus:ring-4 focus:ring-blue-100"><option value="recent">Plus récentes</option><option value="older">Plus anciennes</option></select></div>
        </div></Reveal>

        <div className="flex items-center gap-2 overflow-x-auto py-5" role="tablist" aria-label="Catégories d’actualités">
          <span className="mr-1 inline-flex shrink-0 items-center gap-1.5 text-xs font-extrabold uppercase tracking-wide text-slate-400"><SlidersHorizontal className="h-3.5 w-3.5" /> Rubriques</span>
          <button type="button" role="tab" aria-selected={activeCategory === "all"} onClick={() => setActiveCategory("all")} className={`shrink-0 rounded-full px-4 py-2 text-sm font-bold transition focus:outline-none focus:ring-2 focus:ring-haiti-blue ${activeCategory === "all" ? "bg-haiti-blue text-white shadow-md shadow-haiti-blue/15" : "bg-white text-slate-600 hover:bg-blue-50 hover:text-haiti-blue"}`}>Toutes</button>
          {categories.data?.map((category) => <button key={category.id} type="button" role="tab" aria-selected={activeCategory === category.slug} onClick={() => setActiveCategory(category.slug)} className={`shrink-0 rounded-full px-4 py-2 text-sm font-bold transition focus:outline-none focus:ring-2 focus:ring-haiti-blue ${activeCategory === category.slug ? "bg-haiti-red text-white shadow-md shadow-haiti-red/15" : "bg-white text-slate-600 hover:bg-red-50 hover:text-haiti-red"}`}>{category.nom}</button>)}
        </div>

        {articles.isLoading ? <div className="rounded-3xl border border-slate-200 bg-white p-10"><Loader label="Chargement des actualités…" /></div> : articles.isError ? <ErrorState error={articles.error} /> : !filteredArticles.length ? <div className="rounded-3xl border border-slate-200 bg-white p-8"><EmptyState label={search ? "Aucun article ne correspond à votre recherche." : "Aucun article n’est encore publié dans cette rubrique."} /></div> : <>
          <div className="mb-4 flex items-center justify-between text-xs font-semibold text-slate-400"><span>{filteredArticles.length} {filteredArticles.length > 1 ? "articles" : "article"}</span><span className="inline-flex items-center gap-1"><Trophy className="h-3.5 w-3.5" /> Football haïtien et international</span></div>
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">{remainingStories.map((article, index) => <Reveal key={article.id} delay={(index % 3) * 0.05}><StoryCard article={article} /></Reveal>)}</div>
          {remainingStories.length === 0 && <p className="rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-7 text-center text-sm text-slate-500">Vous êtes à jour. Les prochains articles seront ajoutés ici.</p>}
        </>}
      </section>

      {filExterne.data?.length > 0 && <section className="mt-16 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"><Reveal><div className="mb-6 flex flex-wrap items-end justify-between gap-4"><div><p className="text-[11px] font-extrabold uppercase tracking-[.2em] text-haiti-red">Ailleurs dans le sport</p><h2 className="mt-2 font-display text-2xl font-black text-haiti-ink">À suivre chez nos sources</h2></div><p className="max-w-md text-sm leading-6 text-slate-500">Une sélection de liens vers les publications de médias partenaires.</p></div></Reveal><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{filExterne.data.map((item) => <a key={item.id} href={item.url} target="_blank" rel="noreferrer" className="group rounded-2xl border border-slate-100 bg-slate-50/70 p-5 transition hover:-translate-y-0.5 hover:border-blue-100 hover:bg-white hover:shadow-lg"><p className="text-[11px] font-extrabold uppercase tracking-[.14em] text-haiti-red">{item.source}</p><h3 className="mt-2 font-display font-black leading-snug text-haiti-ink group-hover:text-haiti-blue">{item.titre}</h3>{item.resume && <p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-600">{item.resume}</p>}<span className="mt-4 inline-flex items-center gap-1 text-xs font-extrabold text-haiti-blue">Lire à la source <ArrowUpRight className="h-3.5 w-3.5" /></span></a>)}</div></section>}
    </main>
  </div>;
}
