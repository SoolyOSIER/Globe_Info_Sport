import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams, useBlocker } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import DOMPurify from "dompurify";
import api from "../api/axiosClient";
import { save } from "../api/resources";
import { useDetail, useList, usePage } from "../hooks/useResources";
import { useAuthStore } from "../store/authStore";
import { can } from "../utils/roleHierarchy";
import { ErrorMessage, Loading } from "../components/ui/UI";
import ResourcePage from "./ResourcePage";
import "../newsroom.css";

const labels = { BROUILLON: "Brouillon", A_VALIDER: "À valider", PROGRAMME: "Programmé", PUBLIE: "Publié", ARCHIVE: "Archivé" };
const blank = { titre: "", slug: "", chapo: "", contenu: "", categorie: "", sport: "", pays: [], clubs: [], competitions: [], athletes: [], selections: [], tags: [], galerie: [], video_urls: [], source: "", titre_seo: "", description_seo: "", legende_image: "", a_la_une: false, breaking: false, recommande: false, sponsorise: false };

export function NewsroomPage() {
  const [statut, setStatut] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const articles = usePage("articles", { statut, search, page, page_size: 12 });
  return <div className="newsroom"><header className="desk-hero"><div><p className="desk-eyebrow">Globe Info Sport / La rédaction</p><h1>Les histoires commencent ici.</h1><p>Du terrain à la publication. Une rédaction ouverte à tous les sports et à tous les continents.</p><Link className="desk-primary" to="/articles/nouveau">Écrire un article</Link></div></header><section className="news-panel"><div className="news-filters"><label>Rechercher<input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} placeholder="Titre, sujet…" /></label><label>État éditorial<select value={statut} onChange={e => { setStatut(e.target.value); setPage(1); }}><option value="">Tous les contenus</option>{Object.entries(labels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label></div>{articles.isLoading ? <Loading /> : articles.isError ? <ErrorMessage error={articles.error} /> : <><div className="news-stories">{articles.data?.results.map(article => <Link className="news-story" to={`/articles/${article.id}/modifier`} key={article.id}><span className={`news-status status-${article.statut}`}>{labels[article.statut]}</span><h2>{article.titre}</h2><p>{article.chapo}</p><small>{article.categorie?.nom} · {article.auteur?.nom} · {new Date(article.updated_at).toLocaleDateString("fr")}</small></Link>)}</div>{!articles.data?.count && <p>Aucun article dans cette sélection. Votre prochaine histoire peut commencer maintenant.</p>}<div className="news-actions"><button disabled={!articles.data?.previous} onClick={() => setPage(page - 1)}>Précédent</button><span>Page {page} · {articles.data?.count || 0} articles</span><button disabled={!articles.data?.next} onClick={() => setPage(page + 1)}>Suivant</button></div></>}</section></div>;
}

function ReferenceSelect({ resource, label, value, onChange, multiple = false, required = false }) {
  const query = useList(resource, { page_size: 200 });
  return <label>{label}<select multiple={multiple} value={value ?? (multiple ? [] : "")} required={required} onChange={e => onChange(multiple ? Array.from(e.target.selectedOptions, o => Number(o.value)) : e.target.value)}>{!multiple && <option value="">Sélectionner…</option>}{query.data?.map(item => <option key={item.id} value={item.id}>{item.nom_complet || item.nom || item.legende || `Image ${item.id}`}</option>)}</select>{query.isError && <small role="alert">Référentiel indisponible. <button type="button" onClick={() => query.refetch()}>Réessayer</button></small>}</label>;
}

function RichEditor({ value, onChange, disabled }) {
  const ref = useRef(null);
  useEffect(() => { if (ref.current && ref.current.innerHTML !== value) ref.current.innerHTML = DOMPurify.sanitize(value); }, [value]);
  const command = (name, argument) => { ref.current.focus(); document.execCommand(name, false, argument); onChange(ref.current.innerHTML); };
  return <div className="rich-editor"><div className="rich-toolbar" role="toolbar" aria-label="Mise en forme">{[["bold", "Gras"], ["italic", "Italique"], ["insertUnorderedList", "Liste"], ["insertOrderedList", "Liste numérotée"], ["formatBlock", "Citation", "blockquote"], ["formatBlock", "H1", "h1"], ["formatBlock", "H2", "h2"], ["formatBlock", "H3", "h3"], ["formatBlock", "Paragraphe", "p"], ["insertHorizontalRule", "Séparation"]].map(([name, label, argument]) => <button type="button" key={label} onMouseDown={e => e.preventDefault()} onClick={() => command(name, argument)}>{label}</button>)}<button type="button" onMouseDown={e => e.preventDefault()} onClick={() => { const url = window.prompt("Adresse du lien (https://…)"); if (url && /^https?:\/\//i.test(url)) command("createLink", url); }}>Lien</button><button type="button" onMouseDown={e => e.preventDefault()} onClick={() => { const url = window.prompt("Adresse de l’image (https://…)"); if (url && /^https?:\/\//i.test(url)) command("insertImage", url); }}>Image</button><button type="button" onMouseDown={e => e.preventDefault()} onClick={() => command("insertHTML", "<table><thead><tr><th>Colonne 1</th><th>Colonne 2</th></tr></thead><tbody><tr><td>Donnée</td><td>Donnée</td></tr></tbody></table>")}>Tableau</button></div><div ref={ref} contentEditable={!disabled} suppressContentEditableWarning className="rich-content" role="textbox" aria-multiline="true" aria-label="Contenu de l’article" onInput={e => onChange(e.currentTarget.innerHTML)} onPaste={e => { e.preventDefault(); command("insertHTML", DOMPurify.sanitize(e.clipboardData.getData("text/html") || e.clipboardData.getData("text/plain").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll("\n", "<br>"))); }} /></div>;
}

export function ArticleEditorPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const client = useQueryClient();
  const article = useDetail("articles", id);
  const user = useAuthStore(s => s.user);
  const editor = can(user, "EDITEUR_EN_CHEF");
  const [form, setForm] = useState(blank);
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(false);
  const [date, setDate] = useState("");
  const [message, setMessage] = useState("");
  const [comment, setComment] = useState("");
  const [dirty, setDirty] = useState(false);
  const loadedId = useRef(null);
  const unsaved = useRef(false);
  const blocker = useBlocker(({ currentLocation, nextLocation }) => unsaved.current && currentLocation.pathname !== nextLocation.pathname);
  useEffect(() => { if (blocker.state === "blocked") { if (window.confirm("Quitter sans enregistrer les modifications ?")) blocker.proceed(); else blocker.reset(); } }, [blocker]);
  const [imagePreview, setImagePreview] = useState("");
  useEffect(() => { if (!image) { setImagePreview(""); return; } const url = URL.createObjectURL(image); setImagePreview(url); return () => URL.revokeObjectURL(url); }, [image]);
  const internal = Boolean(id && article.data && (editor || article.data.auteur?.id === user?.id));
  const history = useList(`articles/${id}/historique`, {}, { enabled: internal });
  const comments = useList(`articles/${id}/commentaires`, {}, { enabled: internal });
  useEffect(() => {
    const routeChanged = loadedId.current !== id;
    if (routeChanged) { setImage(null); setDirty(false); unsaved.current = false; setMessage(""); loadedId.current = id; }
    if (!article.data) { if (!id) setForm(blank); return; }
    if (dirty && !routeChanged) return;
    const data = article.data;
    setForm({ ...blank, ...Object.fromEntries(Object.keys(blank).map(key => [key, key === "categorie" ? data.categorie?.id || "" : key === "tags" ? data.tags.map(t => t.id) : key === "video_urls" ? data.videos?.map(video => video.url_embed) || [] : data[key] ?? blank[key]])) });
    setDirty(false); unsaved.current = false;
  }, [article.data, id]);
  useEffect(() => { const warn = e => { if (dirty) { e.preventDefault(); e.returnValue = ""; } }; window.addEventListener("beforeunload", warn); return () => window.removeEventListener("beforeunload", warn); }, [dirty]);
  const update = (key, value) => { setForm(f => ({ ...f, [key]: value })); setDirty(true); unsaved.current = true; setMessage(""); };
  const mutation = useMutation({ mutationFn: async action => {
    if (action === "commentaires") return api.post(`/articles/${id}/commentaires/`, { texte: comment });
    if (action === "save") {
      const payload = { ...form, sport: form.sport || null };
      if (image) { const body = new FormData(); body.append("payload", JSON.stringify(payload)); body.append("image_une", image); return save("articles", body, id); }
      return save("articles", payload, id);
    }
    return api.post(`/articles/${id}/${action}/`, action === "programmer" ? { date_publication: new Date(date).toISOString() } : {});
  }, onSuccess: (result, action) => { setMessage(action === "save" ? "Article enregistré." : "Action effectuée."); if (action !== "commentaires") { setDirty(false); unsaved.current = false; } if (action === "save") setImage(null); setComment(""); if (action !== "commentaires") client.invalidateQueries({ queryKey: ["articles"] }); if (internal) { history.refetch(); comments.refetch(); } if (!id && result.id) navigate(`/articles/${result.id}/modifier`, { replace: true }); }, });
  if (id && article.isLoading) return <Loading />;
  if (id && article.isError) return <ErrorMessage error={article.error} />;
  const editable = !id || editor || (article.data?.auteur?.id === user?.id && ["BROUILLON", "A_VALIDER"].includes(article.data?.statut));
  const textField = (key, label, maxLength, required = false) => <>{key === "source" && <label>Vidéos liées (une URL par ligne)<textarea value={form.video_urls.join("\n")} placeholder="https://www.youtube.com/watch?v=…" onChange={e => update("video_urls", e.target.value.split("\n").map(url => url.trim()).filter(Boolean))} /></label>}<label>{label}<input value={form[key]} maxLength={maxLength} required={required} onChange={e => update(key, e.target.value)} /></label></>;
  return <div className="newsroom"><header className="news-editor-heading"><div><Link to="/articles" >← Salle de rédaction</Link><p className="desk-eyebrow">{id ? labels[article.data?.statut] : "Nouvel article"}</p><h1>{id ? "Affiner votre histoire." : "Une nouvelle histoire."}</h1></div><button type="button" onClick={() => setPreview(!preview)}>{preview ? "Revenir à l’éditeur" : "Prévisualiser"}</button></header>{mutation.isError && <ErrorMessage error={mutation.error} />}{message && <p className="news-success" role="status">{message}</p>}
    {preview ? <article className="news-panel news-preview"><p>{form.sponsorise && "Contenu sponsorisé"}</p><h1>{form.titre || "Votre titre"}</h1><p className="news-chapo">{form.chapo}</p>{(imagePreview || article.data?.image_une) && <img src={imagePreview || article.data.image_une} alt={form.legende_image} />}<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(form.contenu) }} /><p>{form.source && `Source : ${form.source}`}</p></article> : <form onSubmit={e => { e.preventDefault(); mutation.mutate("save"); }}><fieldset disabled={!editable || mutation.isPending}><div className="news-editor-grid"><section className="news-panel news-writing">{textField("titre", "Titre de l’article", 250, true)}<label>Chapeau<textarea maxLength={300} value={form.chapo} onChange={e => update("chapo", e.target.value)} required /></label><label>Corps de l’article</label><RichEditor disabled={!editable || mutation.isPending} value={form.contenu} onChange={value => update("contenu", value)} /><label>Image à la une<input type="file" accept="image/*" onChange={e => { setImage(e.target.files[0]); setDirty(true); unsaved.current = true; }} /></label>{textField("legende_image", "Légende de l’image", 300)}{textField("source", "Source / attribution", 200)}<details><summary>Référencement et adresse</summary>{textField("slug", "Slug (automatique si vide)", 270)}{textField("titre_seo", "Titre SEO", 250)}{textField("description_seo", "Description SEO", 320)}</details></section><aside className="news-panel"><h2>Classer & relier</h2><ReferenceSelect resource="categories" label="Type de contenu" value={form.categorie} required onChange={v => update("categorie", v)} /><ReferenceSelect resource="sports" label="Sport" value={form.sport} onChange={v => update("sport", v)} />{[["pays", "Pays"], ["competitions", "Championnats / compétitions"], ["clubs", "Clubs"], ["selections", "Sélections"], ["athletes", "Athlètes"], ["tags", "Tags"], ["galerie", "Galerie d’images"]].map(([key, label]) => <ReferenceSelect key={key} resource={key === "athletes" ? "joueurs" : key === "galerie" ? "images" : key} label={label} multiple value={form[key]} onChange={v => update(key, v)} />)}<small>Pour plusieurs choix, utilisez Ctrl / Cmd + clic.</small><h2>Mise en avant</h2>{[["a_la_une", "À la une"], ["breaking", "Breaking News"], ["recommande", "Recommandé"], ["sponsorise", "Contenu sponsorisé"]].map(([key, label]) => <label className="news-check" key={key}><input type="checkbox" checked={form[key]} onChange={e => update(key, e.target.checked)} />{label}</label>)}</aside></div><div className="news-save"><span>{dirty ? "Modifications non enregistrées" : "Votre espace éditorial"}</span><button className="desk-primary" disabled={mutation.isPending}>{mutation.isPending ? "Enregistrement…" : "Enregistrer"}</button></div></fieldset></form>}
    {id && <section className="news-panel"><h2>Publication</h2>{dirty && <p>Enregistrez les modifications avant de changer le statut.</p>}<div className="news-actions">{editable && article.data?.statut === "BROUILLON" && <button disabled={dirty || mutation.isPending} onClick={() => mutation.mutate("soumettre")}>Soumettre à la validation</button>}{editor && <><button disabled={dirty || mutation.isPending || article.data?.statut === "BROUILLON"} onClick={() => mutation.mutate("reprendre")}>Renvoyer en brouillon</button><button disabled={dirty || mutation.isPending} onClick={() => mutation.mutate("publier")}>Publier maintenant</button><button disabled={dirty || mutation.isPending} onClick={() => mutation.mutate("archiver")}>Archiver</button><label>Publication programmée (heure locale)<input type="datetime-local" value={date} onChange={e => setDate(e.target.value)} /></label><button disabled={!date || dirty || mutation.isPending} onClick={() => mutation.mutate("programmer")}>Programmer</button></>}</div></section>}
    {internal && <div className="news-editor-grid"><section className="news-panel"><h2>Discussion interne</h2>{comments.data?.map(item => <blockquote key={item.id}><b>{item.auteur_nom}</b><p>{item.texte}</p></blockquote>)}<form onSubmit={e => { e.preventDefault(); mutation.mutate("commentaires"); }}><label>Votre commentaire<textarea maxLength={5000} required value={comment} onChange={e => setComment(e.target.value)} /></label><button disabled={mutation.isPending}>Ajouter un commentaire</button></form></section><section className="news-panel"><h2>Historique des versions</h2>{history.data?.map(item => <details key={item.id}><summary>{new Date(item.created_at).toLocaleString("fr")} · {item.action} · {item.auteur_nom || "Système"}</summary><h3>{item.donnees.titre}</h3><p>{item.donnees.chapo}</p><div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(item.donnees.contenu || "") }} /></details>)}</section></div>}
  </div>;
}

export function EditorialSettingsPage() {
  return <div className="newsroom"><h1>Référentiels internationaux</h1><p>Faites évoluer la couverture sans modifier le code.</p><ResourcePage title="Sports" resource="sports" fields={[{ name: "nom", label: "Sport", required: true }, { name: "slug", label: "Slug" }]} /><ResourcePage title="Pays" resource="pays" fields={[{ name: "nom", label: "Pays", required: true }, { name: "code", label: "Code pays (HT, FR…)", required: true }, { name: "region", label: "Région", required: true, options: ["Amérique du Nord", "Amérique centrale", "Caraïbes", "Amérique du Sud", "Europe", "Afrique", "Asie", "Océanie"].map(value => ({ value, label: value })) }]} /><ResourcePage title="Types de contenus" resource="categories" fields={[{ name: "nom", label: "Nom", required: true }, { name: "slug", label: "Slug" }]} /><ResourcePage title="Tags" resource="tags" fields={[{ name: "nom", label: "Nom", required: true }, { name: "slug", label: "Slug" }]} /></div>;
}
