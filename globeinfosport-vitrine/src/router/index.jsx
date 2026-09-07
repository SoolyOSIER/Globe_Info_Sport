import { createBrowserRouter } from "react-router-dom";
import PublicLayout from "../layouts/PublicLayout";
import Accueil from "../pages/Accueil";
import Actualites from "../pages/Actualites";
import ArticleDetail from "../pages/ArticleDetail";
import Calendrier from "../pages/Calendrier";
import Championnat from "../pages/Championnat";
import Contact from "../pages/Contact";
import Expatries from "../pages/Expatries";
import Galerie from "../pages/Galerie";
import { Confidentialite, MentionsLegales, NotFound } from "../pages/Legal";

export const router = createBrowserRouter([{ element: <PublicLayout />, children: [
  { index: true, element: <Accueil /> }, { path: "championnat", element: <Championnat /> },
  { path: "actualites", element: <Actualites /> }, { path: "actualites/:slug", element: <ArticleDetail /> },
  { path: "calendrier", element: <Calendrier /> }, { path: "expatries", element: <Expatries /> },
  { path: "galerie", element: <Galerie /> }, { path: "contact", element: <Contact /> },
  { path: "mentions-legales", element: <MentionsLegales /> }, { path: "confidentialite", element: <Confidentialite /> },
  { path: "*", element: <NotFound /> },
] }]);
