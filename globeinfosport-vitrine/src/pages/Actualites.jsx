import { useState } from "react";
import { Link } from "react-router-dom";
import { ErrorState, Loader, SectionTitle, EmptyState } from "../components/common/UI";
import { SEO } from "../components/common/SEO";
import { usePublicQuery } from "../hooks/publicHooks";

export default function Actualites() {
  const [search, setSearch] = useState("");
  const articles = usePublicQuery("articles", "/articles/", { search, page_size: 24 });
  const chiffres = usePublicQuery("chiffres", "/chiffres-cles/", {});
  return <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6"><SEO title="Actualités" /><SectionTitle eyebrow="Information" title="Les dernières nouvelles">Toute l’actualité du football haïtien, mise à jour par la rédaction.</SectionTitle><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Rechercher une actualité" aria-label="Rechercher une actualité" className="mb-8 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-haiti-blue focus:ring-2 focus:ring-blue-100" />{chiffres.data?.length > 0 && <div className="mb-12 grid grid-cols-2 gap-3 md:grid-cols-4">{chiffres.data.map((item) => <div key={item.id} className="rounded-xl bg-haiti-blue p-5 text-white"><p className="font-display text-3xl font-black">{item.valeur}</p><p className="mt-1 text-sm text-blue-100">{item.libelle}</p></div>)}</div>}{articles.isLoading ? <Loader /> : articles.isError ? <ErrorState error={articles.error} /> : !articles.data?.length ? <EmptyState label="Aucun article ne correspond à votre recherche." /> : <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">{articles.data.map((article) => <Link key={article.id} to={`/actualites/${article.slug}`} className="rounded-2xl bg-white p-6 shadow-card transition hover:-translate-y-1"><p className="text-xs font-bold uppercase tracking-wider text-haiti-red">{article.categorie?.nom || "Actualité"}</p><h2 className="mt-2 font-display text-xl font-black text-haiti-ink">{article.titre}</h2><p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-600">{article.chapo}</p><p className="mt-5 text-xs text-slate-400">{article.date_publication && new Date(article.date_publication).toLocaleDateString("fr-HT")}</p></Link>)}</div>}</div>;
}
