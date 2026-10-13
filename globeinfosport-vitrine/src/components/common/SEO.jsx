import { Helmet } from "react-helmet-async";

export function SEO({ title, description = "L’information sportive d’Haïti et du monde entier.", image, article }) {
  const fullTitle = title ? `${title} | Globe Info Sport` : "Globe Info Sport | Le sport sans frontières";
  const canonical = `${import.meta.env.VITE_SITE_URL || window.location.origin}${window.location.pathname}`;
  const structured = article ? { "@context": "https://schema.org", "@type": "NewsArticle", headline: article.titre, description: article.chapo, image: image ? [image] : undefined, datePublished: article.date_publication, dateModified: article.updated_at, author: { "@type": "Person", name: article.auteur_nom || "Rédaction Globe Info Sport" }, publisher: { "@type": "Organization", name: "Globe Info Sport" }, mainEntityOfPage: canonical } : null;
  return <Helmet><title>{fullTitle}</title><meta name="description" content={description} /><link rel="canonical" href={canonical} /><meta property="og:title" content={fullTitle} /><meta property="og:description" content={description} /><meta property="og:url" content={canonical} /><meta property="og:type" content={article ? "article" : "website"} /><meta name="twitter:card" content={image ? "summary_large_image" : "summary"} />{image && <meta property="og:image" content={image} />}{structured && <script type="application/ld+json">{JSON.stringify(structured).replace(/</g, "\\u003c")}</script>}</Helmet>;
}
