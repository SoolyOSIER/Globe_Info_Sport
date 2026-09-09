import { CalendarDays, ChevronRight, Clock3, Trophy } from "lucide-react";
import { motion, useReducedMotion } from "framer-motion";
import { Link } from "react-router-dom";

const FALLBACK_GRADIENTS = [
  "from-haiti-blue via-[#1239b9] to-haiti-ink",
  "from-haiti-red via-[#a70d2a] to-haiti-ink",
  "from-[#0b315b] via-haiti-blue to-[#163a75]",
];

export const nationalCategorySlugs = new Set([
  "selection-nationale",
  "championnat",
]);

export function formatDate(value, options = { dateStyle: "medium" }) {
  if (!value) return "À paraître";
  return new Intl.DateTimeFormat("fr-HT", options).format(new Date(value));
}

export function CategoryBadge({ category, inverse = false }) {
  return (
    <span className={`inline-flex w-fit items-center rounded-full border px-3 py-1 text-[11px] font-extrabold uppercase tracking-[.14em] ${inverse ? "border-white/25 bg-white/10 text-white" : "border-haiti-red/15 bg-red-50 text-haiti-red"}`}>
      {category?.nom ?? "Actualité"}
    </span>
  );
}

export function Reveal({ children, className = "", delay = 0 }) {
  const reducedMotion = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reducedMotion ? false : { opacity: 0, y: 18 }}
      whileInView={reducedMotion ? {} : { opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: 0.48, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

function CardImage({ article, className = "", priority = false }) {
  if (article.image_une) {
    return <img src={article.image_une} alt="" className={`h-full w-full object-cover transition duration-700 group-hover:scale-105 ${className}`} loading={priority ? "eager" : "lazy"} />;
  }
  const gradient = FALLBACK_GRADIENTS[article.id % FALLBACK_GRADIENTS.length];
  return <div className={`grid h-full w-full place-items-center bg-gradient-to-br ${gradient} ${className}`}><Trophy className="h-12 w-12 text-white/40" aria-hidden="true" /></div>;
}

export function StoryCard({ article, featured = false, compact = false, priority = false }) {
  if (!article) return null;
  if (compact) {
    return <Link to={`/actualites/${article.slug}`} className="group flex gap-4 rounded-2xl border border-slate-100 bg-white p-3 transition duration-300 hover:-translate-y-1 hover:shadow-card focus:outline-none focus:ring-2 focus:ring-haiti-red"><div className="h-20 w-24 shrink-0 overflow-hidden rounded-xl"><CardImage article={article} /></div><div className="min-w-0 py-1"><CategoryBadge category={article.categorie} /><h3 className="mt-2 line-clamp-2 font-display text-base font-black leading-snug text-haiti-ink transition group-hover:text-haiti-blue">{article.titre}</h3><p className="mt-1 text-xs font-medium text-slate-500">{formatDate(article.date_publication)}</p></div></Link>;
  }

  return <Link to={`/actualites/${article.slug}`} className={`group relative block overflow-hidden rounded-[1.5rem] bg-white transition duration-300 hover:-translate-y-1 hover:shadow-card focus:outline-none focus:ring-2 focus:ring-haiti-red ${featured ? "min-h-[31rem] shadow-2xl shadow-haiti-ink/20" : "border border-slate-100 shadow-sm"}`}>
    <div className={featured ? "absolute inset-0" : "aspect-[16/10] overflow-hidden"}><CardImage article={article} priority={priority} /></div>
    {featured && <div className="absolute inset-0 bg-gradient-to-t from-haiti-ink via-haiti-ink/35 to-transparent" />}
    <div className={featured ? "absolute inset-x-0 bottom-0 p-6 sm:p-8" : "p-5 sm:p-6"}>
      <CategoryBadge category={article.categorie} inverse={featured} />
      <h3 className={`mt-3 font-display font-black leading-tight ${featured ? "max-w-2xl text-3xl text-white sm:text-4xl" : "text-xl text-haiti-ink group-hover:text-haiti-blue"}`}>{article.titre}</h3>
      <p className={`mt-3 line-clamp-2 text-sm leading-6 ${featured ? "max-w-xl text-slate-200" : "text-slate-600"}`}>{article.chapo}</p>
      <div className={`mt-5 flex items-center justify-between text-xs font-bold ${featured ? "text-white/80" : "text-slate-500"}`}><span className="inline-flex items-center gap-1.5"><CalendarDays className="h-3.5 w-3.5" />{formatDate(article.date_publication)}</span><span className={`inline-flex items-center gap-1 ${featured ? "text-haiti-gold" : "text-haiti-red"}`}>Lire <ChevronRight className="h-4 transition group-hover:translate-x-1" /></span></div>
    </div>
  </Link>;
}

export function StoryMeta({ article, inverse = false }) {
  return <div className={`flex flex-wrap items-center gap-x-4 gap-y-2 text-sm ${inverse ? "text-slate-300" : "text-slate-500"}`}><span className="inline-flex items-center gap-1.5"><CalendarDays className="h-4 w-4" />{formatDate(article.date_publication, { dateStyle: "long" })}</span><span className="inline-flex items-center gap-1.5"><Clock3 className="h-4 w-4" />Lecture éditoriale</span></div>;
}
