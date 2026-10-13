import { Navigate, Outlet, createBrowserRouter, useLocation, useRouteError, Link } from "react-router-dom";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { restoreSession } from "../api/authApi";
import { useAuthStore } from "../store/authStore";
import { can } from "../utils/roleHierarchy";
import MainLayout from "../components/layout/MainLayout";
import { Loading } from "../components/ui/UI";
import { NewsroomPage, ArticleEditorPage, EditorialSettingsPage } from "../pages/NewsroomPage";
import LoginPage from "../pages/LoginPage";
import DashboardPage from "../pages/DashboardPage";
import { FAQPage, NewsletterPage, VitrinePage } from "../pages/PublicationPages";
import { AccountsPage, ClubsEtrangersPage, ClubsPage, CompetitionsPage, ExpatriesPage, GaleriePage, JoueursPage, LegendesPage, MessagesPage, ParcoursClubsPage, SelectionsPage, SyndicationPage, TransfertsPage } from "../pages/ManagementPages";
import ResultatFormPage from "../pages/ResultatFormPage";
import MatchesManagementPage from "../pages/MatchesManagementPage";

function SessionGate() {
  const user = useAuthStore((state) => state.user); const token = useAuthStore((state) => state.accessToken); const hydrated = useAuthStore((state) => state.hydrated); const setSession = useAuthStore((state) => state.setSession); const setHydrated = useAuthStore((state) => state.setHydrated);
  const session = useQuery({ queryKey: ["session"], queryFn: restoreSession, enabled: !token && !hydrated, retry: false, staleTime: Infinity });
  useEffect(() => { if (session.data) setSession(session.data); if (session.isError) setHydrated(); }, [session.data, session.isError, setHydrated, setSession]);
  if (!hydrated && !token) return <main className="grid min-h-screen place-items-center"><Loading /></main>;
  if (!user || !token) return <Navigate to="/login" replace />;
  return <Outlet />;
}
function RoleGate({ role }) { const user = useAuthStore((state) => state.user); const location = useLocation(); return can(user, role) ? <Outlet /> : <Navigate to="/" replace state={{ from: location }} />; }

function RouteErrorPage() {
  const error = useRouteError();
  return <main className="mx-auto max-w-2xl p-8"><h1 className="text-2xl font-bold">Cette page n'a pas pu s'afficher.</h1><p className="my-4">Rechargez la page ou revenez au tableau de bord.</p><pre className="whitespace-pre-wrap text-sm">{error?.message || error?.statusText}</pre><button className="my-4 mr-4 rounded border p-3" onClick={() => window.location.reload()}>Recharger</button><Link to="/">Tableau de bord</Link></main>;
}

export const router = createBrowserRouter([{ errorElement: <RouteErrorPage />, children: [{ path: "/login", element: <LoginPage /> }, { element: <SessionGate />, children: [{ element: <MainLayout />, children: [
  { index: true, element: <DashboardPage /> }, { path: "articles", element: <NewsroomPage /> }, { path: "articles/nouveau", element: <ArticleEditorPage /> }, { path: "articles/:id/modifier", element: <ArticleEditorPage /> }, { path: "joueurs", element: <JoueursPage /> },
  { element: <RoleGate role="EDITEUR_EN_CHEF" />, children: [{ path: "newsletter", element: <NewsletterPage /> }, { path: "faq", element: <FAQPage /> }] },
  { element: <RoleGate role="ADMINISTRATEUR" />, children: [{ path: "referentiels", element: <EditorialSettingsPage /> }, { path: "vitrine", element: <VitrinePage /> }] },
  { path: "championnat/competitions", element: <CompetitionsPage /> }, { path: "championnat/clubs", element: <ClubsPage /> }, { path: "championnat/selections", element: <SelectionsPage /> }, { path: "championnat/clubs/parcours", element: <ParcoursClubsPage /> }, { path: "championnat/matchs", element: <MatchesManagementPage /> }, { path: "championnat/matchs/:id/resultat", element: <ResultatFormPage /> },
  { path: "expatries/clubs", element: <ClubsEtrangersPage /> }, { path: "expatries", element: <ExpatriesPage /> }, { path: "expatries/transferts", element: <TransfertsPage /> }, { path: "galerie", element: <GaleriePage /> },
  { element: <RoleGate role="EDITEUR_EN_CHEF" />, children: [{ path: "sources-externes", element: <SyndicationPage /> }] },
  { element: <RoleGate role="EDITEUR_EN_CHEF" />, children: [{ path: "joueurs/legendes", element: <LegendesPage /> }, { path: "messages-contact", element: <MessagesPage /> }] },
  { element: <RoleGate role="ADMINISTRATEUR" />, children: [{ path: "comptes", element: <AccountsPage /> }] },
] }] }, { path: "*", element: <Navigate to="/" replace /> }]}], { basename: import.meta.env.BASE_URL });
