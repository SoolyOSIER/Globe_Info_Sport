import { ClipboardPenLine } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { ErrorMessage, Loading } from "../components/ui/UI";
import { useList } from "../hooks/useResources";
import ResourcePage from "./ResourcePage";

const fields = [
  { name: "competition", label: "Compétition", required: true },
  { name: "club_domicile", label: "Club domicile", required: true },
  { name: "club_exterieur", label: "Club extérieur" },
  { name: "adversaire_texte", label: "Adversaire (si hors championnat)" },
  { name: "date_heure", label: "Date et heure", type: "datetime-local", required: true },
  { name: "lieu", label: "Lieu" },
  { name: "diffusion_tv", label: "Diffusion TV" },
  { name: "resume", label: "Résumé", type: "textarea", full: true },
];

export default function MatchesManagementPage() {
  const navigate = useNavigate();
  const competitions = useList("competitions", { actif: true, page_size: 100 }, { refetchOnMount: "always" });
  const clubs = useList("clubs", { page_size: 100 }, { refetchOnMount: "always" });
  if (competitions.isLoading || clubs.isLoading) return <Loading />;
  if (competitions.isError) return <ErrorMessage error={competitions.error} />;
  if (clubs.isError) return <ErrorMessage error={clubs.error} />;
  const matchFields = fields.map((field) => {
    if (field.name === "competition") return {
      ...field,
      options: competitions.data.map((competition) => ({
        value: competition.id,
        label: `${competition.nom} · ${competition.saison}`,
      })),
    };
    if (["club_domicile", "club_exterieur"].includes(field.name)) return {
      ...field,
      options: clubs.data.map((club) => ({
        value: club.id,
        label: club.ville ? `${club.nom} · ${club.ville}` : club.nom,
      })),
    };
    return field;
  });
  return <ResourcePage
    title="Calendrier et matchs"
    description="Sélectionnez les noms des équipes et de la compétition, puis ouvrez la feuille de résultat pour mettre à jour automatiquement les tableaux sportifs."
    resource="matchs"
    fields={matchFields}
    format={(row, field) => field.name === "club_domicile" ? row.club_domicile_detail?.nom : field.name === "club_exterieur" ? row.club_exterieur_detail?.nom ?? row.adversaire_texte : undefined}
    rowActions={(match) => <button type="button" onClick={() => navigate(`/championnat/matchs/${match.id}/resultat`)} className="mr-2 inline-flex rounded p-2 text-emerald-700" aria-label="Saisir le résultat"><ClipboardPenLine className="h-4" /></button>}
  />;
}
