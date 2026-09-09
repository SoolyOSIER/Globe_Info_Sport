import DOMPurify from "dompurify";
import { ArrowLeft, ArrowUpRight, Quote } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { ErrorState, Loader, SectionTitle } from "../components/common/UI";
import { CategoryBadge, Reveal, StoryCard, StoryMeta } from "../components/common/Editorial";
import { SEO } from "../components/common/SEO";
import { usePublicQuery } from "../hooks/publicHooks";

export default function ArticleDetail() {
  const { slug } = useParams();
  const article = usePublicQuery("article", `/articles/${slug}/`, {});
  const related = usePublicQuery("related-articles", "/articles/", { categorie: article.data?.categorie?.id, page_size: 4 }, { enabled: Boolean(article.data?.categorie?.id) });
  if (article.isLoading) return <Loader label="Chargement de l’article…" />;
  if (article.isError) return <main className="mx-auto max-w-3xl px-4 py-12"><ErrorState error={article.error} /></main>;
  const data = article.data;
  const relatedStories = (related.data ?? []).filter((item) => item.id !== data.id).slice(0, 3);

  return <div className="page-texture min-h-screen"><SEO title={data.titre} description={data.chapo} /><article><header className="relative overflow-hidden bg-haiti-ink"><div className="hero-grid absolute inset-0 opacity-35" /><div className="absolute -right-16 top-0 h-72 w-72 rounded-full bg-haiti-red/30 blur-3xl" /><div className="relative mx-auto max-w-4xl px-4 py-14 sm:px-6 sm:py-20"><Reveal><Link to="/actualites" className="inline-flex items-center gap-2 text-sm font-extrabold text-haiti-gold transition hover:text-white"><ArrowLeft className="h-4 w-4" />Toutes les actualités</Link><div className="mt-8"><CategoryBadge category={data.categorie} inverse /><h1 className="mt-5 font-display text-4xl font-black leading-[1.06] tracking-tight text-white sm:text-5xl lg:text-6xl">{data.titre}</h1><p className="mt-6 max-w-3xl text-lg leading-8 text-slate-200 sm:text-xl">{data.chapo}</p><div className="mt-7"><StoryMeta article={data} inverse /></div></div></Reveal></div></header>
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6 sm:py-14">{data.image_une && <Reveal><img src={data.image_une} alt="" className="aspect-[16/9] w-full rounded-[1.5rem] object-cover shadow-2xl shadow-haiti-ink/20" /></Reveal>}<Reveal><div className="mx-auto mt-10 max-w-3xl"><div className="prose prose-slate max-w-none text-[1.05rem] leading-8 prose-headings:font-display prose-headings:font-black prose-headings:text-haiti-ink prose-a:text-haiti-blue" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(data.contenu) }} />{data.source && <p className="mt-10 border-l-4 border-haiti-gold bg-white px-5 py-4 text-sm text-slate-600"><b className="text-haiti-ink">Source éditoriale :</b> {data.source}</p>}</div></Reveal>
      {data.citations?.length > 0 && <section className="mx-auto mt-14 max-w-3xl space-y-4">{data.citations.map((citation) => <Reveal key={citation.id}><blockquote className="rounded-2xl bg-haiti-blue p-6 text-white"><Quote className="h-7 w-7 text-haiti-gold" /><p className="mt-4 font-display text-xl font-black leading-relaxed">« {citation.texte} »</p><footer className="mt-4 text-sm text-blue-100">{citation.auteur_nom}{citation.auteur_fonction ? ` · ${citation.auteur_fonction}` : ""}</footer></blockquote></Reveal>)}</section>}
      {data.videos?.length > 0 && <section className="mx-auto mt-14 max-w-3xl"><Reveal><SectionTitle eyebrow="À voir" title="Vidéos liées" /></Reveal><div className="space-y-3">{data.videos.map((video) => <a key={video.id} className="flex items-center justify-between gap-4 rounded-2xl border border-slate-100 bg-white p-5 font-bold text-haiti-blue transition hover:-translate-y-0.5 hover:shadow-card" href={video.url_embed} target="_blank" rel="noreferrer"><span>{video.titre}</span><ArrowUpRight className="h-5 shrink-0 text-haiti-red" /></a>)}</div></section>}
    </div></article>
    {relatedStories.length > 0 && <section className="border-t border-slate-200 bg-white"><div className="mx-auto max-w-7xl px-4 py-14 sm:px-6"><Reveal><SectionTitle eyebrow="Même rubrique" title="Continuer la lecture" /></Reveal><div className="grid gap-5 md:grid-cols-3">{relatedStories.map((item, index) => <Reveal key={item.id} delay={index * 0.06}><StoryCard article={item} /></Reveal>)}</div></div></section>}
  </div>;
}
