import DOMPurify from "dompurify";
import { Link, useParams } from "react-router-dom";
import { ErrorState, Loader } from "../components/common/UI";
import { SEO } from "../components/common/SEO";
import { usePublicQuery } from "../hooks/publicHooks";

export default function ArticleDetail() {
  const { slug } = useParams(); const article = usePublicQuery("article", `/articles/${slug}/`, {});
  if (article.isLoading) return <Loader />; if (article.isError) return <main className="mx-auto max-w-3xl px-4 py-12"><ErrorState error={article.error} /></main>;
  const data = article.data;
  return <article className="mx-auto max-w-3xl px-4 py-14 sm:px-6"><SEO title={data.titre} description={data.chapo} /><Link to="/actualites" className="text-sm font-bold text-haiti-red">← Toutes les actualités</Link><p className="mt-8 text-xs font-bold uppercase tracking-wider text-haiti-red">{data.categorie?.nom || "Actualité"}</p><h1 className="mt-3 font-display text-4xl font-black leading-tight text-haiti-ink sm:text-5xl">{data.titre}</h1><p className="mt-5 text-xl leading-8 text-slate-600">{data.chapo}</p>{data.image_une && <img src={data.image_une} alt="" className="mt-8 aspect-video w-full rounded-2xl object-cover shadow-card" />}<div className="prose prose-slate mt-10 max-w-none prose-headings:font-display prose-headings:text-haiti-ink" dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(data.contenu) }} />{data.videos?.length > 0 && <section className="mt-12"><h2 className="font-display text-2xl font-black">Vidéos liées</h2>{data.videos.map((video) => <a key={video.id} className="mt-3 block rounded-lg border p-4 font-bold text-haiti-blue" href={video.url_embed} target="_blank" rel="noreferrer">{video.titre}</a>)}</section>}</article>;
}
