import { lazy, Suspense } from "react";
import { createBrowserRouter } from "react-router-dom";
import { Loader } from "../components/common/UI";
import PublicLayout from "../layouts/PublicLayout";

const Explorer = lazy(() => import("../pages/Explorer"));
const Television = lazy(() => import("../pages/Television"));
const Accueil = lazy(() => import("../pages/Accueil"));
const APropos = lazy(() => import("../pages/APropos"));
const Actualites = lazy(() => import("../pages/Actualites"));
const ArticleDetail = lazy(() => import("../pages/ArticleDetail"));
const Calendrier = lazy(() => import("../pages/Calendrier"));
const Championnat = lazy(() => import("../pages/Championnat"));
const ClubDetail = lazy(() => import("../pages/ClubDetail"));
const CompetitionDetail = lazy(() => import("../pages/CompetitionDetail"));
const SelectionDetail = lazy(() => import("../pages/SelectionDetail"));
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
  { path: "haiti", element: page(Explorer) },
  { path: "international", element: page(Explorer) },
  { path: "recherche", element: page(Explorer) },
  { path: "tv", element: page(Television) },
  { index: true, element: page(Accueil) },
  { path: "a-propos", element: page(APropos) },
  { path: "championnat", element: page(Championnat) },
  { path: "clubs/:slug", element: page(ClubDetail) },
  { path: "competitions/:id", element: page(CompetitionDetail) },
  { path: "selections/:id", element: page(SelectionDetail) },
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
