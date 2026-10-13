import { useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, Edit3, FileText, Plus, Search, Trash2 } from "lucide-react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { ErrorMessage, Loading, Modal } from "../components/ui/UI";
import { usePage, useResourceMutations } from "../hooks/useResources";
import { retrieve } from "../api/resources";
import { useAuthStore } from "../store/authStore";
import { can } from "../utils/roleHierarchy";
import { initialValues, prepareValues } from "../utils/resourceForms";
import { useUiStore } from "../store/uiStore";

const emptyValue = (field) => field.defaultValue ?? (field.type === "checkbox" ? false : field.multiple ? [] : "");
const statusLabels = { BROUILLON: "Brouillon", A_VALIDER: "À valider", PROGRAMME: "Programmé", PUBLIE: "Publié", ARCHIVE: "Archivé" };

function Field({ field, values, setValues, isArticle, editing }) {
  const value = values[field.name] ?? emptyValue(field);
  const change = (next) => setValues({ ...values, [field.name]: next });
  let control;
  if (field.type === "textarea") control = <textarea readOnly={field.readOnly} required={field.required} value={value} onChange={(event) => change(event.target.value)} rows={isArticle ? 10 : 5} />;
  else if (field.type === "checkbox") control = <input disabled={field.readOnly} type="checkbox" checked={Boolean(value)} onChange={(event) => change(event.target.checked)} />;
  else if (field.options) control = <select disabled={field.readOnly} multiple={field.multiple} required={field.required} value={value} onChange={(event) => change(field.multiple ? Array.from(event.target.selectedOptions, (option) => option.value) : event.target.value)}>
    {!field.multiple && <option value="">Sélectionner</option>}
    {field.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
  </select>;
  else control = <input readOnly={field.readOnly} type={field.type || "text"} required={field.required && !(editing && ["file", "password"].includes(field.type))} value={field.type === "file" ? undefined : value} accept={field.type === "file" ? "image/*" : undefined} onChange={(event) => change(field.type === "file" ? event.target.files?.[0] : event.target.value)} />;
  return <label className={field.full ? "resource-field-full" : ""}>
    {field.label}{field.required && !(editing && ["file", "password"].includes(field.type)) ? " *" : ""}{control}
    {field.multiple && <small>Maintenez Ctrl ou Cmd pour choisir plusieurs éléments.</small>}
    {field.type === "file" && typeof value === "string" && value && <small>Image existante conservée si aucun fichier n’est choisi.</small>}
  </label>;
}

export default function ResourcePage({ title, description, resource, fields, readOnly = false, allowCreate = !readOnly, allowDelete = !readOnly, format, rowActions }) {
  const user = useAuthStore(state => state.user);
  const minimumRole = ["sports", "pays", "selections", "utilisateurs", "pages-contenu", "partenaires"].includes(resource) ? "ADMINISTRATEUR" : ["competitions", "clubs", "parcours-clubs", "clubs-etrangers", "joueurs-expatries", "transferts", "legendes", "categories", "tags", "videos", "citations", "faq", "messages-contact", "flux-syndication"].includes(resource) ? "EDITEUR_EN_CHEF" : "REDACTEUR";
  readOnly = readOnly || !can(user, minimumRole);
  allowCreate = allowCreate && !readOnly;
  allowDelete = allowDelete && !readOnly;
  const [search, setSearch] = useState(""); const [term, setTerm] = useState(""); const [page, setPage] = useState(1); const [status, setStatus] = useState(""); const [editing, setEditing] = useState(null); const [formOpen, setFormOpen] = useState(false); const [values, setValues] = useState({}); const [opening, setOpening] = useState(false); const [openError, setOpenError] = useState(null);
  const request = useRef(0); const { id } = useParams(); const { pathname } = useLocation(); const navigate = useNavigate();
  const query = usePage(resource, { page, page_size: 10, ...(term ? { search: term } : {}), ...(status ? { statut: status } : {}) }); const mutations = useResourceMutations(resource); const pushToast = useUiStore((state) => state.pushToast); const rows = query.data?.results ?? []; const columns = fields.filter((field) => field.type !== "textarea" && field.type !== "password" && field.type !== "file").slice(0, 5); const isArticle = resource === "articles";
  useEffect(() => { const timer = setTimeout(() => { setTerm(search.trim()); setPage(1); }, 300); return () => clearTimeout(timer); }, [search]);
  const open = async (row = null) => { const current = ++request.current; setOpenError(null); mutations.save.reset(); setOpening(true); try { const full = row?.id ? await retrieve(resource, row.id) : null; if (current !== request.current) return; setEditing(full); setValues(initialValues(fields, full)); setFormOpen(true); } catch (error) { if (current === request.current) setOpenError(error); } finally { if (current === request.current) setOpening(false); } };
  useEffect(() => { if (isArticle && (id || pathname.endsWith("/nouveau"))) open(id ? { id } : null); return () => { request.current += 1; }; }, [resource, id, pathname]);
  const close = () => { if (mutations.save.isPending) return; setFormOpen(false); if (isArticle && (id || pathname.endsWith("/nouveau"))) navigate("/articles", { replace: true }); };
  const submit = (event) => {
    event.preventDefault();
    if (readOnly) return;
    mutations.save.mutate({ values: prepareValues(fields, values, Boolean(editing)), id: editing?.id }, {
      onSuccess: () => {
        setFormOpen(false);
        pushToast("Enregistrement effectu\u00e9.");
      },
    });
  };
  const cell = (row, field) => { const custom = format?.(row, field); if (custom !== undefined) return custom; const value = row[field.name]; if (field.type === "checkbox") return <span className={`desk-badge ${value ? "desk-badge-blue" : ""}`}>{value ? "Oui" : "Non"}</span>; if (Array.isArray(value)) return value.length ? value.join(", ") : "—"; if (typeof value === "object") return value?.nom ?? value?.email ?? "—"; return field.options?.find((option) => String(option.value) === String(value))?.label ?? String(value ?? "—"); };
  return <section className="resource-workspace">
    {readOnly && resource !== "newsletter" && <p className="rounded-lg bg-blue-50 p-3 text-sm">Consultation uniquement avec votre compte actuel.</p>}
    <div className="resource-heading"><div><p className="desk-eyebrow">L’atelier / Gestion</p><h1>{title}</h1><p>{description || `Retrouvez, organisez et mettez à jour les informations de la rubrique ${title.toLowerCase()}.`}</p></div>{allowCreate && <button type="button" onClick={() => open()} className="desk-primary"><Plus size={17} />Ajouter</button>}</div>
    <div className="resource-toolbar"><label className="resource-search"><Search size={18} /><input aria-label={`Rechercher dans ${title}`} value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Rechercher…" /></label>{isArticle && <select aria-label="Filtrer par statut" value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }}><option value="">Tous les statuts</option>{Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select>}<span role="status">{query.isLoading ? "Chargement…" : query.isError ? "Indisponible" : `${query.data?.count ?? 0} résultat(s)`}</span></div>
    {opening && <Loading />}{openError && <ErrorMessage error={openError} />}{mutations.remove.isError && <ErrorMessage error={mutations.remove.error} />}
    {query.isLoading ? <Loading /> : query.isError ? <ErrorMessage error={query.error} /> : <div className="resource-table-wrap"><table className="resource-table"><caption className="sr-only">{title} — page {page}</caption><thead><tr>{columns.map((field) => <th scope="col" key={field.name}>{field.label}</th>)}{isArticle && <th scope="col">Statut</th>}{!readOnly && <th scope="col">Actions</th>}</tr></thead><tbody>{rows.length ? rows.map((row) => <tr key={row.id}>{columns.map((field) => <td key={field.name}>{cell(row, field)}</td>)}{isArticle && <td><span className={`desk-badge ${row.statut === "PUBLIE" ? "desk-badge-blue" : ""}`}>{statusLabels[row.statut] || row.statut}</span></td>}{!readOnly && <td><div className="resource-row-actions"><button disabled={opening} type="button" onClick={() => open(row)} aria-label={`Modifier ${row.titre || row.nom || title}`}><Edit3 size={16} /></button>{rowActions?.(row)}{allowDelete && <button disabled={mutations.remove.isPending} type="button" onClick={() => { if (window.confirm("Supprimer cet élément ?")) mutations.remove.mutate(row.id, { onSuccess: () => { if (rows.length === 1 && page > 1) setPage(page - 1); pushToast("Élément supprimé."); } }); }} className="text-haiti-red" aria-label={`Supprimer ${row.titre || row.nom || title}`}><Trash2 size={16} /></button>}</div></td>}</tr>) : <tr><td colSpan={columns.length + Number(isArticle) + Number(!readOnly)}><div className="resource-empty"><FileText size={32} /><h2>{term || status ? "Aucun résultat pour ces filtres" : "Cette rubrique attend son premier contenu"}</h2><p>{term || status ? "Essayez un autre mot-clé ou réinitialisez les filtres." : "Les informations enregistrées apparaîtront ici."}</p>{(term || status) && <button onClick={() => { setSearch(""); setTerm(""); setStatus(""); setPage(1); }}>Réinitialiser</button>}</div></td></tr>}</tbody></table><div className="resource-pagination"><span>Page {page} sur {Math.max(1, Math.ceil((query.data?.count ?? 0) / 10))}</span><div><button disabled={!query.data?.previous} onClick={() => setPage(page - 1)} aria-label="Page précédente"><ChevronLeft size={17} />Précédent</button><button disabled={!query.data?.next} onClick={() => setPage(page + 1)} aria-label="Page suivante">Suivant<ChevronRight size={17} /></button></div></div></div>}
    {formOpen && <Modal title={editing?.id ? `Modifier · ${title}` : `Ajouter · ${title}`} onClose={close}><form onSubmit={submit} className="resource-form"><p className="resource-form-note">{editing ? "Complétez les informations puis enregistrez vos modifications." : "Préparez une fiche complète pour enrichir Globe Info Sport."} Les champs marqués * sont obligatoires.</p>{fields.map((field) => <Field key={field.name} field={field} values={values} setValues={setValues} isArticle={isArticle} editing={editing} />)}{mutations.save.isError && <div className="resource-field-full"><ErrorMessage error={mutations.save.error} /></div>}<div className="resource-form-actions"><button type="button" disabled={mutations.save.isPending} onClick={close}>Annuler</button><button disabled={mutations.save.isPending} className="desk-primary">{mutations.save.isPending ? "Enregistrement…" : "Enregistrer"}</button></div></form></Modal>}
  </section>;
}
