import { usePublicQuery } from "../hooks/publicHooks";
import { SEO } from "../components/common/SEO";
import { Loader, ErrorState } from "../components/common/UI";

import { youtubeEmbed } from "../utils/video";
export default function Television() {
  const videos = usePublicQuery("tv", "/videos/", { page_size: 24 });
  return <section className="mx-auto max-w-7xl px-5 py-14"><SEO title="Globe Info Sport TV" description="Interviews, reportages, analyses et émissions de Globe Info Sport." /><p className="font-bold uppercase tracking-widest text-haiti-red">Le sport se raconte aussi en images</p><h1 className="mt-4 text-4xl font-black md:text-6xl">Globe Info Sport TV</h1><p className="my-6 text-lg text-slate-600">Interviews, reportages, analyses et rendez-vous de la rédaction.</p><a className="inline-block rounded-xl bg-haiti-red px-5 py-3 font-bold text-white" href="https://www.youtube.com/@GlobeInfosports21" target="_blank" rel="noreferrer">Notre chaîne YouTube ↗</a>{videos.isLoading ? <Loader /> : videos.isError ? <ErrorState error={videos.error} /> : <div className="mt-10 grid gap-8 md:grid-cols-2">{videos.data?.map(video => <article key={video.id} className="overflow-hidden rounded-2xl border bg-white">{youtubeEmbed(video.url_embed) && <iframe className="aspect-video w-full" src={youtubeEmbed(video.url_embed)} title={video.titre} loading="lazy" allowFullScreen referrerPolicy="strict-origin-when-cross-origin" />}<h2 className="p-5 text-xl font-bold"><a href={video.url_embed} target="_blank" rel="noreferrer">{video.titre} ↗</a></h2></article>)}{!videos.data?.length && <p>Les prochaines vidéos sélectionnées par la rédaction apparaîtront ici. Retrouvez nos publications sur la chaîne officielle.</p>}</div>}</section>;
}
