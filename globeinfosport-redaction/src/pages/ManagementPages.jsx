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
  joueurs: [{ name: "nom", label: "Nom", required: true }, { name: "prenom", label: "Prénom" }, { name: "poste", label: "Poste (si applicable)" }, { name: "club_actuel", label: "Club actuel" }, { name: "numero_maillot", label: "N° maillot", type: "number" }, { name: "photo", label: "Photo", type: "file" }, { name: "biographie", label: "Biographie", type: "textarea", full: true }, { name: "selection_nationale", label: "Sélection nationale", type: "checkbox" }, { name: "emblematique", label: "Emblématique", type: "checkbox" }],
  legendes: [{ name: "nom", label: "Nom", required: true }, { name: "periode_active", label: "Période" }, { name: "poste", label: "Poste" }, { name: "photo", label: "Photo", type: "file" }, { name: "biographie", label: "Biographie", type: "textarea", required: true, full: true }, { name: "exploits", label: "Exploits", type: "textarea", full: true }, { name: "ordre_affichage", label: "Ordre", type: "number" }],
  competitions: [{ name: "nom", label: "Nom", required: true }, { name: "type", label: "Type", required: true, options: [{ value: "CHAMPIONNAT_NATIONAL", label: "Championnat national" }, { value: "ELIMINATOIRES_CDM", label: "Éliminatoires CDM" }, { value: "LIGUE_NATIONS", label: "Ligue des Nations" }, { value: "AUTRE", label: "Autre" }] }, { name: "saison", label: "Saison", required: true }, { name: "actif", label: "Active", type: "checkbox", defaultValue: true }],
  clubs: [{ name: "nom", label: "Nom", required: true }, { name: "ville", label: "Ville" }, { name: "stade", label: "Stade" }, { name: "fondation", label: "Fondation", type: "number" }, { name: "couleurs", label: "Couleurs du club" }, { name: "site_web", label: "Site officiel", type: "url" }, { name: "logo", label: "Logo", type: "file" }, { name: "description", label: "Présentation du club", type: "textarea", full: true }, { name: "histoire", label: "Histoire du club", type: "textarea", full: true }, { name: "palmares", label: "Palmarès", type: "textarea", full: true }],
  "clubs-etrangers": [{ name: "nom", label: "Nom", required: true }, { name: "pays", label: "Pays", required: true }, { name: "ligue", label: "Ligue" }, { name: "logo", label: "Logo", type: "file" }],
  "joueurs-expatries": [{ name: "joueur", label: "Joueur", required: true }, { name: "club_etranger", label: "Club étranger", required: true }, { name: "date_arrivee", label: "Date d’arrivée", type: "date" }, { name: "statut", label: "Statut", defaultValue: "ACTIF", options: [{ value: "ACTIF", label: "Actif" }, { value: "PRETE", label: "Prêté" }, { value: "BLESSE", label: "Blessé" }, { value: "LIBRE", label: "Libre" }] }, { name: "en_vedette", label: "En vedette", type: "checkbox" }],
  transferts: [{ name: "joueur", label: "Joueur", required: true }, { name: "club_origine", label: "Club origine", required: true }, { name: "club_destination", label: "Club destination", required: true }, { name: "date_transfert", label: "Date", type: "date", required: true }, { name: "type_transfert", label: "Type", defaultValue: "DEFINITIF", options: [{ value: "DEFINITIF", label: "Définitif" }, { value: "PRET", label: "Prêt" }] }, { name: "montant", label: "Montant" }, { name: "source", label: "Source" }],
  albums: [{ name: "titre", label: "Titre", required: true }, { name: "match_lie", label: "Match lié" }, { name: "description", label: "Description", type: "textarea", full: true }],
  images: [{ name: "album", label: "Album", required: true }, { name: "image", label: "Photo", type: "file", required: true }, { name: "legende", label: "Légende", full: true }, { name: "ordre", label: "Ordre", type: "number" }],
  partenaires: [{ name: "nom", label: "Nom", required: true }, { name: "logo", label: "Logo", type: "file", required: true }, { name: "url", label: "Lien" }, { name: "ordre", label: "Ordre", type: "number" }, { name: "actif", label: "Actif", type: "checkbox" }],
  faq: [{ name: "question", label: "Question", required: true, full: true }, { name: "reponse", label: "Réponse", type: "textarea", required: true, full: true }, { name: "ordre", label: "Ordre", type: "number" }],
  "pages-contenu": [{ name: "cle", label: "Clé", required: true }, { name: "titre", label: "Titre", required: true }, { name: "image", label: "Image", type: "file" }, { name: "contenu", label: "Contenu", type: "textarea", required: true, full: true }, { name: "actif", label: "Actif", type: "checkbox" }],
  utilisateurs: [{ name: "identifiant", label: "Identifiant", required: true }, { name: "nom", label: "Nom", required: true }, { name: "prenom", label: "Prénom" }, { name: "email", label: "Email", type: "email" }, { name: "role_redaction", label: "Rôle", required: true }, { name: "password", label: "Mot de passe", type: "password", required: true }],
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
  return <ResourcePage title="Articles" description="Les nouveaux contenus sont des brouillons. Un éditeur en chef les publie sur la vitrine." resource="articles" allowDelete={can(user, "EDITEUR_EN_CHEF")} fields={articleFields} format={(row, field) => field.name === "categorie" ? row.categorie?.nom : field.name === "statut" ? row.statut : undefined} rowActions={(article) => can(user, "EDITEUR_EN_CHEF") && article.statut !== "PUBLIE" ? <button type="button" disabled={publishArticle.isPending} onClick={() => publishArticle.mutate(article.id)} className="mr-2 rounded bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-700 disabled:opacity-50" aria-label={`Publier ${article.titre}`}>Publier</button> : null} />;
};
export const JoueursPage = () => {
  const postes = useList("postes");
  const sports = useList("sports", { page_size: 200 });
  const pays = useList("pays", { page_size: 200 });
  if (postes.isLoading || sports.isLoading || pays.isLoading) return <Loading />;
  if (postes.isError || sports.isError || pays.isError) return <ErrorMessage error={postes.error || sports.error || pays.error} />;
  const joueurFields = fields.joueurs.map((field) => field.name === "poste" ? {
    ...field,
    label: "Poste",
    options: postes.data.map((poste) => ({ value: poste.id, label: poste.nom })),
  } : field);
  return <ResourcePage title="Joueurs et athlètes" resource="joueurs" fields={[...joueurFields, { name: "sport", label: "Sport", options: sports.data.map(item => ({ value: item.id, label: item.nom })) }, { name: "pays", label: "Pays", options: pays.data.map(item => ({ value: item.id, label: item.nom })) }]} format={(row, field) => field.name === "poste" ? row.poste?.nom : field.name === "nom" ? row.nom_complet : undefined} />;
};
export const LegendesPage = () => <ResourcePage title="Légendes" resource="legendes" fields={fields.legendes} />;
const footballDataNotConfigured = (error) => String(error?.response?.data?.detail || "").includes("FOOTBALL_DATA_API_TOKEN");
export const CompetitionsPage = () => {
  const sports = useList("sports", { page_size: 200 }); const pays = useList("pays", { page_size: 200 }); const clubs = useList("clubs", { page_size: 200 });
  const user = useAuthStore((state) => state.user);
  const pushToast = useUiStore((state) => state.pushToast);
  const queryClient = useQueryClient();
  const synchroniser = useMutation({
    mutationFn: () => api.post("/competitions/synchroniser-donnees/"),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ["competitions"] });
      queryClient.invalidateQueries({ queryKey: ["clubs"] });
      queryClient.invalidateQueries({ queryKey: ["matchs"] });
      queryClient.invalidateQueries({ queryKey: ["public"] });
      const resume = response.data;
      pushToast(`${resume.competitions} championnat(s) actualisé(s), ${resume.matchs} match(s) synchronisé(s).`);
    },
    onError: (error) => pushToast(footballDataNotConfigured(error)
      ? "Ajoutez votre clé football-data.org dans globeinfosport-backend/.env, puis relancez les services."
      : error?.response?.data?.detail || "La synchronisation des données sportives a échoué."),
  });
  if (sports.isLoading || pays.isLoading || clubs.isLoading) return <Loading />;
  if (sports.isError || pays.isError || clubs.isError) return <ErrorMessage error={sports.error || pays.error || clubs.error} />;
  const competitionFields = [...fields.competitions.slice(0, 3), { name: "sport", label: "Sport", options: sports.data.map((item) => ({ value: item.id, label: item.nom })) }, { name: "pays", label: "Pays", options: pays.data.map((item) => ({ value: item.id, label: item.nom })) }, { name: "clubs", label: "Clubs participants", multiple: true, full: true, options: clubs.data.map((item) => ({ value: item.id, label: item.nom })) }, { name: "description", label: "Présentation", type: "textarea", full: true }, { name: "logo", label: "Logo", type: "file" }, fields.competitions[3]];
  return <div className="space-y-6">
    {can(user, "EDITEUR_EN_CHEF") && <section className="rounded-2xl border border-blue-100 bg-blue-50 p-5">
      <p className="font-bold text-haiti-ink">Données automatiques des cinq grands championnats</p>
      <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600">Actualisez les équipes, le calendrier, les scores et le classement de Premier League, Liga, Serie A, Bundesliga et Ligue 1 depuis la source sportive configurée.</p>
      <p className="mt-3 rounded-lg border border-blue-100 bg-white/75 px-3 py-2 text-xs font-medium leading-5 text-slate-600">Première utilisation : ouvrez <code>globeinfosport-backend/.env</code>, renseignez <code>FOOTBALL_DATA_API_TOKEN</code>, puis relancez le démarrage local.</p>
      <button type="button" disabled={synchroniser.isPending} onClick={() => synchroniser.mutate()} className="mt-4 rounded-lg bg-haiti-blue px-4 py-2 text-sm font-bold text-white disabled:opacity-50">
        {synchroniser.isPending ? "Synchronisation en cours…" : "Synchroniser maintenant"}
      </button>
    </section>}
    <ResourcePage title="Compétitions" description="Répertoriez les championnats, leurs équipes participantes et les tournois de tous les pays et de tous les sports." resource="competitions" fields={competitionFields} />
  </div>;
};
export const ClubsPage = () => {
  const sports = useList("sports", { page_size: 200 }); const pays = useList("pays", { page_size: 200 });
  if (sports.isLoading || pays.isLoading) return <Loading />;
  if (sports.isError || pays.isError) return <ErrorMessage error={sports.error || pays.error} />;
  const clubFields = [fields.clubs[0], { name: "sport", label: "Sport", options: sports.data.map((item) => ({ value: item.id, label: item.nom })) }, { name: "pays", label: "Pays", options: pays.data.map((item) => ({ value: item.id, label: item.nom })) }, { name: "entraineur", label: "Entraîneur" }, ...fields.clubs.slice(1)];
  return <ResourcePage title="Clubs" description="Créez les fiches complètes : identité, pays, sport, histoire, palmarès et informations pratiques." resource="clubs" fields={clubFields} />;
};
export const SelectionsPage = () => {
  const sports = useList("sports", { page_size: 200 }); const pays = useList("pays", { page_size: 200 }); const joueurs = useList("joueurs", { page_size: 200 }); const competitions = useList("competitions", { page_size: 200 });
  if (sports.isLoading || pays.isLoading || joueurs.isLoading || competitions.isLoading) return <Loading />;
  if (sports.isError || pays.isError || joueurs.isError || competitions.isError) return <ErrorMessage error={sports.error || pays.error || joueurs.error || competitions.error} />;
  const selectionFields = [{ name: "nom", label: "Nom", required: true }, { name: "pays", label: "Pays", required: true, options: pays.data.map((item) => ({ value: item.id, label: item.nom })) }, { name: "sport", label: "Sport", required: true, options: sports.data.map((item) => ({ value: item.id, label: item.nom })) }, { name: "entraineur", label: "Entraîneur" }, { name: "logo", label: "Logo", type: "file" }, { name: "histoire", label: "Histoire et présentation", type: "textarea", full: true }, { name: "joueurs", label: "Joueurs / athlètes", multiple: true, full: true, options: joueurs.data.map((item) => ({ value: item.id, label: item.nom_complet })) }, { name: "competitions", label: "Compétitions suivies", multiple: true, full: true, options: competitions.data.map((item) => ({ value: item.id, label: `${item.nom} · ${item.saison}` })) }];
  return <ResourcePage title="Sélections nationales" description="Préparez les fiches des équipes nationales, leurs effectifs et les compétitions associées." resource="selections" fields={selectionFields} />;
};
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
export const ExpatriesPage = () => {
  const joueurs = useList("joueurs", { page_size: 200 }); const clubs = useList("clubs-etrangers", { page_size: 200 });
  if (joueurs.isLoading || clubs.isLoading) return <Loading />;
  if (joueurs.isError || clubs.isError) return <ErrorMessage error={joueurs.error || clubs.error} />;
  const expatFields = fields["joueurs-expatries"].map((field) => field.name === "joueur" ? { ...field, options: joueurs.data.map((item) => ({ value: item.id, label: item.nom_complet })) } : field.name === "club_etranger" ? { ...field, options: clubs.data.map((item) => ({ value: item.id, label: `${item.nom} · ${item.pays}` })) } : field);
  return <ResourcePage title="Joueurs expatriés" resource="joueurs-expatries" fields={expatFields} format={(row, field) => field.name === "joueur" ? row.joueur_nom : field.name === "club_etranger" ? row.club_etranger_detail?.nom : undefined} />;
};
export const TransfertsPage = () => {
  const joueurs = useList("joueurs", { page_size: 200 });
  if (joueurs.isLoading) return <Loading />;
  if (joueurs.isError) return <ErrorMessage error={joueurs.error} />;
  const transfertFields = fields.transferts.map((field) => field.name === "joueur" ? { ...field, options: joueurs.data.map((item) => ({ value: item.id, label: item.nom_complet })) } : field);
  return <ResourcePage title="Transferts" resource="transferts" fields={transfertFields} format={(row, field) => field.name === "joueur" ? row.joueur_nom : undefined} />;
};
export const GaleriePage = () => {
  const matchs = useList("matchs", { page_size: 200 }); const albums = useList("albums", { page_size: 200 });
  if (matchs.isLoading || albums.isLoading) return <Loading />;
  if (matchs.isError || albums.isError) return <ErrorMessage error={matchs.error || albums.error} />;
  const albumFields = fields.albums.map((field) => field.name === "match_lie" ? { ...field, options: matchs.data.map((item) => ({ value: item.id, label: `${item.club_domicile_detail?.nom || "Équipe"} – ${item.club_exterieur_detail?.nom || item.adversaire_texte || "Adversaire"}` })) } : field);
  const imageFields = fields.images.map((field) => field.name === "album" ? { ...field, options: albums.data.map((item) => ({ value: item.id, label: item.titre })) } : field);
  return <div className="space-y-10"><ResourcePage title="Albums" resource="albums" fields={albumFields} /><ResourcePage title="Images" resource="images" fields={imageFields} format={(row, field) => field.name === "album" ? row.album_titre : undefined} /></div>;
};
export const MessagesPage = () => <ResourcePage title="Messages de contact" description="Consultez le message puis marquez-le comme traité après réponse." resource="messages-contact" allowCreate={false} allowDelete={false} fields={[{ name: "nom", label: "Nom", readOnly: true }, { name: "email", label: "Email", readOnly: true }, { name: "sujet", label: "Sujet", readOnly: true }, { name: "message", label: "Message", type: "textarea", full: true, readOnly: true }, { name: "traite", label: "Traité", type: "checkbox" }]} />;
export const AccountsPage = () => {
  const roles = useList("roles");
  if (roles.isLoading) return <Loading />;
  if (roles.isError) return <ErrorMessage error={roles.error} />;
  return <ResourcePage title="Comptes de la rédaction" resource="utilisateurs" fields={fields.utilisateurs.map(field => field.name === "role_redaction" ? { ...field, options: roles.data.map(role => ({ value: role.id, label: role.libelle })) } : field)} format={(row, field) => field.name === "role_redaction" ? row.role_redaction?.libelle : undefined} />;
};
export const ClubsEtrangersPage = () => <ResourcePage title="Clubs internationaux des expatriés" resource="clubs-etrangers" fields={fields["clubs-etrangers"]} />;
