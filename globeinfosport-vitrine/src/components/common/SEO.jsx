import { Helmet } from "react-helmet-async";

export function SEO({ title, description = "Toute la passion du football haïtien." }) {
  const fullTitle = title ? `${title} | Globe Info Sport` : "Globe Info Sport | Football haïtien";
  return <Helmet><title>{fullTitle}</title><meta name="description" content={description} /><meta property="og:title" content={fullTitle} /><meta property="og:description" content={description} /></Helmet>;
}
