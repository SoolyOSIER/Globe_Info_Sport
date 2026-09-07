import { useUiStore } from "../store";
import { ErrorState, Loader, SectionTitle, EmptyState } from "../components/common/UI";
import { SEO } from "../components/common/SEO";
import { usePublicQuery } from "../hooks/publicHooks";

export default function Galerie() {
  const gallery = usePublicQuery("gallery", "/galerie/", { page_size: 100 }); const openImage = useUiStore((state) => state.openImage);
  return <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6"><SEO title="Galerie" /><SectionTitle eyebrow="En images" title="La galerie du football haïtien" />{gallery.isLoading ? <Loader /> : gallery.isError ? <ErrorState error={gallery.error} /> : !gallery.data?.length ? <EmptyState label="La galerie est en cours de préparation." /> : <div className="columns-1 gap-4 sm:columns-2 lg:columns-3">{gallery.data.map((photo) => <button key={photo.id} type="button" className="mb-4 block w-full overflow-hidden rounded-xl bg-slate-200 text-left shadow-card" onClick={() => openImage(photo)}><img src={photo.image} alt={photo.legende || "Photo de la galerie"} className="w-full transition hover:scale-105" /><span className="block p-3 text-sm font-medium text-haiti-ink">{photo.legende || photo.album_titre || "Globe Info Sport"}</span></button>)}</div>}</div>;
}
