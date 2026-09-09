import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../api/axiosClient";
import { ErrorMessage, Loading } from "../components/ui/UI";
import { useDetail, useList } from "../hooks/useResources";
import { useAuthStore } from "../store/authStore";
import { can } from "../utils/roleHierarchy";
import { useUiStore } from "../store/uiStore";
import ResourcePage from "./ResourcePage";

const fields = {
  articles: [{ name: "titre", label: "Titre", required: true, full: true }, { name: "categorie", label: "Catégorie", required: true }, { name: "chapo", label: "Chapeau", required: true, full: true }, { name: "contenu", label: "Contenu", type: "textarea", required: true, full: true }, { name: "image_une", label: "Image à la une", type: "file" }, { name: "a_la_une", label: "À la une", type: "checkbox" }, { name: "source", label: "Source" }],
  joueurs: [{ name: "nom", label: "Nom", required: true }, { name: "prenom", label: "Prénom" }, { name: "poste", label: "ID poste", type: "number", required: true }, { name: "club_actuel", label: "Club actuel" }, { name: "numero_maillot", label: "N° maillot", type: "number" }, { name: "photo", label: "Photo", type: "file" }, { name: "biographie", label: "Biographie", type: "textarea", full: true }, { name: "selection_nationale", label: "Sélection nationale", type: "checkbox" }, { name: "emblematique", label: "Emblématique", type: "checkbox" }],
  legendes: [{ name: "nom", label: "Nom", required: true }, { name: "periode_active", label: "Période" }, { name: "poste", label: "Poste" }, { name: "photo", label: "Photo", type: "file" }, { name: "biographie", label: "Biographie", type: "textarea", required: true, full: true }, { name: "exploits", label: "Exploits", type: "textarea", full: true }, { name: "ordre_affichage", label: "Ordre", type: "number" }],
  competitions: [{ name: "nom", label: "Nom", required: true }, { name: "type", label: "Type", required: true, options: [{ value: "CHAMPIONNAT_NATIONAL", label: "Championnat national" }, { value: "ELIMINATOIRES_CDM", label: "Éliminatoires CDM" }, { value: "LIGUE_NATIONS", label: "Ligue des Nations" }, { value: "AUTRE", label: "Autre" }] }, { name: "saison", label: "Saison", required: true }, { name: "actif", label: "Active", type: "checkbox" }],
  clubs: [{ name: "nom", label: "Nom", required: true }, { name: "ville", label: "Ville" }, { name: "stade", label: "Stade" }, { name: "fondation", label: "Fondation", type: "number" }, { name: "couleurs", label: "Couleurs du club" }, { name: "site_web", label: "Site officiel", type: "url" }, { name: "logo", label: "Logo", type: "file" }, { name: "description", label: "Présentation du club", type: "textarea", full: true }, { name: "histoire", label: "Histoire du club", type: "textarea", full: true }, { name: "palmares", label: "Palmarès", type: "textarea", full: true }],
  "clubs-etrangers": [{ name: "nom", label: "Nom", required: true }, { name: "pays", label: "Pays", required: true }, { name: "ligue", label: "Ligue" }, { name: "logo", label: "Logo", type: "file" }],
  "joueurs-expatries": [{ name: "joueur", label: "ID joueur", type: "number", required: true }, { name: "club_etranger", label: "ID club étranger", type: "number", required: true }, { name: "date_arrivee", label: "Date d’arrivée", type: "date" }, { name: "statut", label: "Statut", options: [{ value: "ACTIF", label: "Actif" }, { value: "PRETE", label: "Prêté" }, { value: "BLESSE", label: "Blessé" }, { value: "LIBRE", label: "Libre" }] }, { name: "en_vedette", label: "En vedette", type: "checkbox" }],
  transferts: [{ name: "joueur", label: "ID joueur", type: "number", required: true }, { name: "club_origine", label: "Club origine", required: true }, { name: "club_destination", label: "Club destination", required: true }, { name: "date_transfert", label: "Date", type: "date", required: true }, { name: "type_transfert", label: "Type", options: [{ value: "DEFINITIF", label: "Définitif" }, { value: "PRET", label: "Prêt" }] }, { name: "montant", label: "Montant" }, { name: "source", label: "Source" }],
  albums: [{ name: "titre", label: "Titre", required: true }, { name: "match_lie", label: "ID match", type: "number" }, { name: "description", label: "Description", type: "textarea", full: true }],
  images: [{ name: "album", label: "ID album", type: "number", required: true }, { name: "image", label: "Photo", type: "file", required: true }, { name: "legende", label: "Légende", full: true }, { name: "ordre", label: "Ordre", type: "number" }],
  partenaires: [{ name: "nom", label: "Nom", required: true }, { name: "logo", label: "Logo", type: "file", required: true }, { name: "url", label: "Lien" }, { name: "ordre", label: "Ordre", type: "number" }, { name: "actif", label: "Actif", type: "checkbox" }],
  faq: [{ name: "question", label: "Question", required: true, full: true }, { name: "reponse", label: "Réponse", type: "textarea", required: true, full: true }, { name: "ordre", label: "Ordre", type: "number" }],
  "pages-contenu": [{ name: "cle", label: "Clé", required: true }, { name: "titre", label: "Titre", required: true }, { name: "image", label: "Image", type: "file" }, { name: "contenu", label: "Contenu", type: "textarea", required: true, full: true }, { name: "actif", label: "Actif", type: "checkbox" }],
  utilisateurs: [{ name: "identifiant", label: "Identifiant", required: true }, { name: "nom", label: "Nom", required: true }, { name: "prenom", label: "Prénom" }, { name: "email", label: "Email", type: "email" }, { name: "role_redaction", label: "ID rôle", type: "number", required: true }, { name: "password", label: "Mot de passe", type: "password" }],
};
export const ArticlesPage = () => {
  // Un référentiel peut avoir été ajouté pendant une session ouverte : il est
  // donc toujours rafraîchi à l'arrivée sur la gestion des articles.
  const categories = useList("categories", {}, { refetchOnMount: "always" });
  const user = useAuthStore((state) => state.user);
  const pushToast = useUiStore((state) => state.pushToast);
  const queryClient = useQueryClient();
  const publishArticle = useMutation({
    mutationFn: (articleId) => api.post(`/articles/${articleId}/publier/`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["articles"] });
      queryClient.invalidateQueries({ queryKey: ["public", "articles"] });
      pushToast("Article publié sur la vitrine.");
    },
    onError: (error) => pushToast(
      error?.response?.data?.detail || "La publication de l’article a échoué.",
    ),
  });
  if (categories.isLoading) return <Loading />;
  if (categories.isError) return <ErrorMessage error={categories.error} />;
  const articleFields = fields.articles.map((field) => field.name === "categorie" ? {
    ...field,
    options: categories.data.map((category) => ({ value: category.id, label: category.nom })),
  } : field);
  return <ResourcePage title="Articles" description="Les nouveaux contenus sont des brouillons. Un éditeur en chef les publie sur la vitrine." resource="articles" fields={articleFields} format={(row, field) => field.name === "categorie" ? row.categorie?.nom : field.name === "statut" ? row.statut : undefined} rowActions={(article) => can(user, "EDITEUR_EN_CHEF") && article.statut !== "PUBLIE" ? <button type="button" disabled={publishArticle.isPending} onClick={() => publishArticle.mutate(article.id)} className="mr-2 rounded bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-700 disabled:opacity-50" aria-label={`Publier ${article.titre}`}>Publier</button> : null} />;
};
export const JoueursPage = () => {
  const postes = useList("postes");
  if (postes.isLoading) return <Loading />;
  if (postes.isError) return <ErrorMessage error={postes.error} />;
  const joueurFields = fields.joueurs.map((field) => field.name === "poste" ? {
    ...field,
    label: "Poste",
    options: postes.data.map((poste) => ({ value: poste.id, label: poste.nom })),
  } : field);
  return <ResourcePage title="Joueurs" resource="joueurs" fields={joueurFields} format={(row, field) => field.name === "poste" ? row.poste?.nom : field.name === "nom" ? row.nom_complet : undefined} />;
};
export const LegendesPage = () => <ResourcePage title="Légendes" resource="legendes" fields={fields.legendes} />;
export const CompetitionsPage = () => <ResourcePage title="Compétitions" resource="competitions" fields={fields.competitions} />;
export const ClubsPage = () => <ResourcePage title="Clubs" description="Créez les fiches complètes : identité, histoire, palmarès et informations pratiques." resource="clubs" fields={fields.clubs} />;
export const ParcoursClubsPage = () => {
  const clubs = useList("clubs", {}, { refetchOnMount: "always" });
  if (clubs.isLoading) return <Loading />;
  if (clubs.isError) return <ErrorMessage error={clubs.error} />;
  const parcoursFields = [{ name: "club", label: "Club", required: true, options: clubs.data.map((club) => ({ value: club.id, label: club.nom })) }, { name: "saison", label: "Saison", required: true }, { name: "competition", label: "Compétition", required: true }, { name: "position_finale", label: "Position / distinction" }, { name: "bilan", label: "Bilan" }, { name: "recit", label: "Récit de la saison", type: "textarea", full: true }, { name: "ordre", label: "Ordre", type: "number" }];
  return <ResourcePage title="Parcours des clubs" description="Ajoutez les saisons, titres, finales et moments marquants : ils alimentent automatiquement les fiches publiques des équipes." resource="parcours-clubs" fields={parcoursFields} format={(row, field) => field.name === "club" ? clubs.data.find((club) => club.id === row.club)?.nom : undefined} />;
};
export const SyndicationPage = () => {
  const categories = useList("categories", {}, { refetchOnMount: "always" });
  const pushToast = useUiStore((state) => state.pushToast);
  const synchroniser = useMutation({ mutationFn: () => api.post("/flux-syndication/synchroniser/"), onSuccess: () => pushToast("Synchronisation des flux lancée."), onError: () => pushToast("Impossible de lancer la synchronisation.") });
  if (categories.isLoading) return <Loading />;
  if (categories.isError) return <ErrorMessage error={categories.error} />;
  const fluxFields = [{ name: "nom", label: "Nom de la source", required: true }, { name: "url", label: "URL RSS autorisée", type: "url", required: true, full: true }, { name: "categorie", label: "Rubrique", options: categories.data.map((category) => ({ value: category.id, label: category.nom })) }, { name: "actif", label: "Flux actif", type: "checkbox" }];
  return <div className="space-y-6"><div className="rounded-2xl border border-blue-100 bg-blue-50 p-5"><p className="font-bold text-haiti-ink">Fil externe attribué</p><p className="mt-1 text-sm leading-6 text-slate-600">Ajoutez uniquement des flux RSS dont la republication sous forme de titre, extrait et lien est autorisée. Les contenus restent liés à leur média d’origine.</p><button type="button" disabled={synchroniser.isPending} onClick={() => synchroniser.mutate()} className="mt-4 rounded-lg bg-haiti-blue px-4 py-2 text-sm font-bold text-white disabled:opacity-50">{synchroniser.isPending ? "Synchronisation…" : "Synchroniser maintenant"}</button></div><ResourcePage title="Sources RSS" description="Les nouveaux éléments sont affichés sur la vitrine comme liens externes attribués." resource="flux-syndication" fields={fluxFields} format={(row, field) => field.name === "categorie" ? categories.data.find((category) => category.id === row.categorie)?.nom : undefined} /></div>;
};
export const ExpatriesPage = () => <ResourcePage title="Joueurs expatriés" resource="joueurs-expatries" fields={fields["joueurs-expatries"]} />;
export const TransfertsPage = () => <ResourcePage title="Transferts" resource="transferts" fields={fields.transferts} />;
export const GaleriePage = () => <div className="space-y-10"><ResourcePage title="Albums" resource="albums" fields={fields.albums} /><ResourcePage title="Images" resource="images" fields={fields.images} /></div>;
export const MessagesPage = () => <ResourcePage title="Messages de contact" description="Marquez un message comme traité après réponse." resource="messages-contact" fields={[{ name: "nom", label: "Nom" }, { name: "email", label: "Email" }, { name: "sujet", label: "Sujet" }, { name: "message", label: "Message", type: "textarea", full: true }, { name: "traite", label: "Traité", type: "checkbox" }]} />;
export const AccountsPage = () => <div className="space-y-10"><ResourcePage title="Comptes rédaction" resource="utilisateurs" fields={fields.utilisateurs} /><ResourcePage title="Partenaires" resource="partenaires" fields={fields.partenaires} /><ResourcePage title="FAQ" resource="faq" fields={fields.faq} /><ResourcePage title="Contenus Accueil" resource="pages-contenu" fields={fields["pages-contenu"]} /></div>;

export function MatchesPage() { const matches = useList("matchs"); return <ResourcePage title="Calendrier et matchs" description="Créez un match, puis saisissez son résultat final dans la page dédiée." resource="matchs" fields={[{ name: "competition", label: "ID compétition", type: "number", required: true }, { name: "club_domicile", label: "ID club domicile", type: "number", required: true }, { name: "club_exterieur", label: "ID club extérieur", type: "number" }, { name: "adversaire_texte", label: "Adversaire (si hors championnat)" }, { name: "date_heure", label: "Date et heure", type: "datetime-local", required: true }, { name: "lieu", label: "Lieu" }, { name: "diffusion_tv", label: "Diffusion TV" }, { name: "resume", label: "Résumé", type: "textarea", full: true }]} format={(row, field) => field.name === "club_domicile" ? row.club_domicile_detail?.nom : field.name === "club_exterieur" ? row.club_exterieur_detail?.nom ?? row.adversaire_texte : undefined} />; }

export function ResultatPage() { const [id, setId] = useState(""); const [home, setHome] = useState(""); const [away, setAway] = useState(""); const [resume, setResume] = useState(""); const [buteurs, setButeurs] = useState("[]"); const client = useQueryClient(); const mutation = useMutation({ mutationFn: (payload) => api.post(`/matchs/${id}/saisir-resultat/`, payload), onSuccess: () => { client.invalidateQueries({ queryKey: ["matchs"] }); client.invalidateQueries({ queryKey: ["classement"] }); } }); const submit = (event) => { event.preventDefault(); try { mutation.mutate({ score_domicile: Number(home), score_exterieur: Number(away), resume, buteurs: JSON.parse(buteurs) }); } catch { alert("La liste des buteurs doit être du JSON valide. Exemple : [{\"joueur\": 1, \"minute\": 42, \"type_but\": \"BUT\"}]"); } }; return <div className="max-w-2xl"><h1 className="font-display text-3xl font-black text-haiti-ink">Saisir un résultat</h1><p className="mt-2 text-sm text-slate-500">La validation recalcule immédiatement le classement et les statistiques.</p><form onSubmit={submit} className="mt-6 grid gap-4 rounded-2xl bg-white p-6 shadow-panel"><label className="text-sm font-bold">ID match<input required type="number" value={id} onChange={(event) => setId(event.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label><div className="grid grid-cols-2 gap-4"><label className="text-sm font-bold">Score domicile<input required min="0" type="number" value={home} onChange={(event) => setHome(event.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label><label className="text-sm font-bold">Score extérieur<input required min="0" type="number" value={away} onChange={(event) => setAway(event.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label></div><label className="text-sm font-bold">Buteurs (liste JSON)<textarea value={buteurs} onChange={(event) => setButeurs(event.target.value)} rows="5" className="mt-1 w-full rounded-lg border p-3 font-mono text-xs" /></label><label className="text-sm font-bold">Résumé<textarea value={resume} onChange={(event) => setResume(event.target.value)} rows="5" className="mt-1 w-full rounded-lg border p-3" /></label>{mutation.isError && <ErrorMessage error={mutation.error} />}<button disabled={mutation.isPending} className="rounded-lg bg-haiti-red py-3 font-bold text-white">{mutation.isPending ? "Validation…" : "Valider le résultat"}</button>{mutation.isSuccess && <p className="text-sm font-bold text-emerald-700">Résultat enregistré et calculs lancés.</p>}</form></div>; }
