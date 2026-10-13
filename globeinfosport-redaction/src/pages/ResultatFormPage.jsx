import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import api from "../api/axiosClient";
import { ErrorMessage, Loading } from "../components/ui/UI";
import { useDetail, useList } from "../hooks/useResources";

const emptyGoal = () => ({ joueur: "", passeur: "", minute: "", type_but: "BUT" });

/** Formulaire éditorial de résultat : aucune saisie JSON n'est demandée. */
export default function ResultatFormPage() {
  const { id: routeId } = useParams();
  const [matchId, setMatchId] = useState(routeId || "");
  const [home, setHome] = useState("");
  const [away, setAway] = useState("");
  const [resume, setResume] = useState("");
  const [goals, setGoals] = useState([emptyGoal()]);
  const players = useList("joueurs", { page_size: 200 });
  const matches = useList("matchs", { page_size: 200 });
  const client = useQueryClient();
  const match = useDetail("matchs", matchId);
  const hydrated = useRef(null);
  useEffect(() => {
    if (!match.data || hydrated.current === matchId) return;
    hydrated.current = matchId;
    setHome(match.data.score_domicile ?? "");
    setAway(match.data.score_exterieur ?? "");
    setResume(match.data.resume || "");
    setGoals(match.data.buteurs?.length ? match.data.buteurs.map(goal => ({ joueur: goal.joueur, passeur: goal.passeur || "", minute: goal.minute, type_but: goal.type_but })) : [emptyGoal()]);
  }, [match.data, matchId]);
  const sortedPlayers = useMemo(
    () => [...(players.data || [])].sort((a, b) => (a.nom_complet || "").localeCompare(b.nom_complet || "")),
    [players.data],
  );
  const mutation = useMutation({
    mutationFn: (payload) => api.post(`/matchs/${matchId}/saisir-resultat/`, payload),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["matchs"] });
      client.invalidateQueries({ queryKey: ["classement"] });
      client.invalidateQueries({ queryKey: ["statistiques"] });
    },
  });

  const updateGoal = (index, field, value) => {
    setGoals((current) => current.map((goal, goalIndex) => (
      goalIndex === index ? { ...goal, [field]: value } : goal
    )));
  };
  const submit = (event) => {
    event.preventDefault();
    mutation.mutate({
      score_domicile: Number(home),
      score_exterieur: Number(away),
      resume,
      buteurs: goals.filter((goal) => goal.joueur && goal.minute !== "").map((goal) => ({
        joueur: Number(goal.joueur),
        ...(goal.passeur ? { passeur: Number(goal.passeur) } : {}),
        minute: Number(goal.minute),
        type_but: goal.type_but,
      })),
    });
  };

  if (players.isLoading || matches.isLoading || (matchId && match.isLoading)) return <Loading />;
  if (players.isError || matches.isError || match.isError) return <ErrorMessage error={players.error || matches.error || match.error} />;
  return <div className="max-w-3xl">
    <h1 className="font-display text-3xl font-black text-haiti-ink">Saisir un résultat</h1>
    <p className="mt-2 text-sm text-slate-500">Le classement, les buteurs et les passes décisives sont recalculés à la validation.</p>
    <form onSubmit={submit} className="mt-6 grid gap-5 rounded-2xl bg-white p-6 shadow-panel">
      <label className="text-sm font-bold">Match
        <select required value={matchId} onChange={(event) => { hydrated.current = null; setMatchId(event.target.value); mutation.reset(); }} className="mt-1 w-full rounded-lg border p-3">
          <option value="">Sélectionner un match</option>{matches.data?.map((match) => <option key={match.id} value={match.id}>{match.club_domicile_detail?.nom || "Équipe"} – {match.club_exterieur_detail?.nom || match.adversaire_texte || "Adversaire"}</option>)}
        </select>
      </label>
      <div className="grid grid-cols-2 gap-4">
        <label className="text-sm font-bold">Score domicile<input required min="0" type="number" value={home} onChange={(event) => setHome(event.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label>
        <label className="text-sm font-bold">Score extérieur<input required min="0" type="number" value={away} onChange={(event) => setAway(event.target.value)} className="mt-1 w-full rounded-lg border p-3" /></label>
      </div>
      <fieldset className="rounded-xl border border-slate-200 p-4">
        <legend className="px-2 font-display text-lg font-black text-haiti-ink">Buteurs</legend>
        <p className="mb-4 text-xs text-slate-500">Laissez la première ligne vide si aucun buteur individuel n’est à ajouter.</p>
        <div className="space-y-3">{goals.map((goal, index) => <div key={index} className="grid gap-2 rounded-lg bg-slate-50 p-3 sm:grid-cols-[1.5fr_1.5fr_.7fr_.9fr_auto]">
          <select aria-label={`Buteur ${index + 1}`} value={goal.joueur} onChange={(event) => updateGoal(index, "joueur", event.target.value)} className="rounded-lg border p-2"><option value="">Buteur</option>{sortedPlayers.map((player) => <option key={player.id} value={player.id}>{player.nom_complet}</option>)}</select>
          <select aria-label={`Passeur ${index + 1}`} value={goal.passeur} onChange={(event) => updateGoal(index, "passeur", event.target.value)} className="rounded-lg border p-2"><option value="">Sans passe</option>{sortedPlayers.map((player) => <option key={player.id} value={player.id}>{player.nom_complet}</option>)}</select>
          <input aria-label={`Minute du but ${index + 1}`} min="0" max="130" type="number" placeholder="Min." value={goal.minute} onChange={(event) => updateGoal(index, "minute", event.target.value)} className="rounded-lg border p-2" />
          <select aria-label={`Type du but ${index + 1}`} value={goal.type_but} onChange={(event) => updateGoal(index, "type_but", event.target.value)} className="rounded-lg border p-2"><option value="BUT">But</option><option value="PENALTY">Penalty</option><option value="CSC">CSC</option></select>
          <button type="button" aria-label="Supprimer le buteur" disabled={goals.length === 1} onClick={() => setGoals((current) => current.filter((_, goalIndex) => goalIndex !== index))} className="rounded-lg px-2 text-haiti-red disabled:opacity-30">×</button>
        </div>)}</div>
        <button type="button" onClick={() => setGoals((current) => [...current, emptyGoal()])} className="mt-3 rounded-lg border border-haiti-blue px-3 py-2 text-sm font-bold text-haiti-blue">+ Ajouter un buteur</button>
      </fieldset>
      <label className="text-sm font-bold">Résumé<textarea value={resume} onChange={(event) => setResume(event.target.value)} rows="5" className="mt-1 w-full rounded-lg border p-3" /></label>
      {mutation.isError && <ErrorMessage error={mutation.error} />}
      <button disabled={mutation.isPending || players.isLoading || matches.isLoading} className="rounded-lg bg-haiti-red py-3 font-bold text-white disabled:opacity-50">{mutation.isPending ? "Validation…" : "Valider le résultat"}</button>
      {mutation.isSuccess && <p role="status" className="text-sm font-bold text-emerald-700">Résultat enregistré et statistiques recalculées.</p>}
    </form>
  </div>;
}
