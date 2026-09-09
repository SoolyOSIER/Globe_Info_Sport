import { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";
import { Loader } from "../components/common/UI";
import PublicLayout from "../layouts/PublicLayout";

const Accueil = lazy(() => import("../pages/Accueil"));
const Actualites = lazy(() => import("../pages/Actualites"));
const ArticleDetail = lazy(() => import("../pages/ArticleDetail"));
const Calendrier = lazy(() => import("../pages/Calendrier"));
const Championnat = lazy(() => import("../pages/Championnat"));
const ClubDetail = lazy(() => import("../pages/ClubDetail"));
const Contact = lazy(() => import("../pages/Contact"));
const Expatries = lazy(() => import("../pages/Expatries"));
const Galerie = lazy(() => import("../pages/Galerie"));
const MentionsLegales = lazy(() => import("../pages/Legal").then((module) => ({ default: module.MentionsLegales })));
const Confidentialite = lazy(() => import("../pages/Legal").then((module) => ({ default: module.Confidentialite })));
const NotFound = lazy(() => import("../pages/Legal").then((module) => ({ default: module.NotFound })));

function page(Component) {
  return <Suspense fallback={<Loader label="Chargement de la page…" />}><Component /></Suspense>;
}

export const router = createBrowserRouter([{ element: <PublicLayout />, children: [
  { index: true, element: page(Accueil) },
  { path: "championnat", element: page(Championnat) },
  { path: "clubs/:slug", element: page(ClubDetail) },
  { path: "actualites", element: page(Actualites) },
  { path: "actualites/:slug", element: page(ArticleDetail) },
  { path: "calendrier", element: page(Calendrier) },
  { path: "expatries", element: page(Expatries) },
  { path: "galerie", element: page(Galerie) },
  { path: "contact", element: page(Contact) },
  { path: "mentions-legales", element: page(MentionsLegales) },
  { path: "confidentialite", element: page(Confidentialite) },
  { path: "*", element: page(NotFound) },
] }]);
