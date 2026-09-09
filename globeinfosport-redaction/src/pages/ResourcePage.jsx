import { useMemo, useState } from "react";
import { Edit3, Plus, Search, Trash2 } from "lucide-react";
import { ErrorMessage, Loading, Modal } from "../components/ui/UI";
import { useList, useResourceMutations } from "../hooks/useResources";
import { useUiStore } from "../store/uiStore";

const emptyValue = (field) => field.type === "checkbox" ? false : "";

export default function ResourcePage({ title, description, resource, fields, readOnly = false, format, rowActions }) {
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState(null);
  const [formOpen, setFormOpen] = useState(false);
  const [values, setValues] = useState({});
  const query = useList(resource, search ? { search } : {});
  const mutations = useResourceMutations(resource);
  const pushToast = useUiStore((state) => state.pushToast);
  const rows = useMemo(() => query.data ?? [], [query.data]);

  const open = (row = null) => {
    setEditing(row);
    setValues(Object.fromEntries(fields.map((field) => {
      const raw = row?.[field.name];
      const value = raw && typeof raw === "object" && "id" in raw ? raw.id : raw;
      return [field.name, value ?? emptyValue(field)];
    })));
    setFormOpen(true);
  };
  const setValue = (name, value) => setValues((current) => ({ ...current, [name]: value }));
  const submit = (event) => {
    event.preventDefault();
    const fileMode = fields.some((field) => field.type === "file" && values[field.name] instanceof File);
    const form = new FormData();
    const plain = {};
    fields.forEach((field) => {
      let value = values[field.name];
      if (field.type === "checkbox") value = Boolean(value);
      if (field.type === "file") { if (value instanceof File) form.append(field.name, value); return; }
      if (value !== "" && value !== null && value !== undefined) { form.append(field.name, value); plain[field.name] = value; }
    });
    mutations.save.mutate({ values: fileMode ? form : plain, id: editing?.id }, {
      onSuccess: () => { setFormOpen(false); pushToast(`${editing ? "Modification" : "Création"} enregistrée.`); },
    });
  };
  const cell = (row, field) => {
    const custom = format?.(row, field); if (custom !== undefined) return custom;
    const value = row[field.name];
    if (field.type === "checkbox") return value ? "Oui" : "Non";
    if (typeof value === "object") return value?.nom ?? value?.email ?? "—";
    return String(value ?? "—");
  };
  return <>
    <div className="mb-7 flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-bold uppercase tracking-wider text-haiti-red">Gestion</p><h1 className="font-display text-3xl font-black text-haiti-ink">{title}</h1>{description && <p className="mt-2 text-sm text-slate-500">{description}</p>}</div>{!readOnly && <button type="button" onClick={() => open()} className="inline-flex items-center gap-2 rounded-lg bg-haiti-blue px-4 py-3 text-sm font-bold text-white"><Plus className="h-4" />Ajouter</button>}</div>
    <div className="mb-4 flex max-w-md items-center rounded-lg border bg-white px-3"><Search className="h-4 text-slate-400" /><input value={search} onChange={(event) => setSearch(event.target.value)} className="w-full bg-transparent px-2 py-3 outline-none" placeholder="Rechercher…" /></div>
    {query.isLoading ? <Loading /> : query.isError ? <ErrorMessage error={query.error} /> : <div className="overflow-x-auto rounded-2xl bg-white shadow-panel"><table className="w-full min-w-[600px] text-left text-sm"><thead className="border-b bg-slate-50"><tr>{fields.slice(0, 5).map((field) => <th key={field.name} className="px-4 py-3 font-bold text-slate-600">{field.label}</th>)}{!readOnly && <th className="px-4 py-3">Actions</th>}</tr></thead><tbody>{rows.length ? rows.map((row) => <tr key={row.id} className="border-b last:border-0">{fields.slice(0, 5).map((field) => <td key={field.name} className="max-w-[220px] truncate px-4 py-3">{cell(row, field)}</td>)}{!readOnly && <td className="px-4 py-3"><button type="button" onClick={() => open(row)} className="mr-2 rounded p-2 text-haiti-blue" aria-label="Modifier"><Edit3 className="h-4" /></button>{rowActions?.(row)}<button type="button" onClick={() => { if (window.confirm("Supprimer cet élément ?")) mutations.remove.mutate(row.id, { onSuccess: () => pushToast("Élément supprimé.") }); }} className="rounded p-2 text-haiti-red" aria-label="Supprimer"><Trash2 className="h-4" /></button></td>}</tr>) : <tr><td colSpan={fields.length + 1} className="p-8 text-center text-slate-500">Aucune donnée.</td></tr>}</tbody></table></div>}
    {formOpen && <Modal title={editing?.id ? `Modifier ${title.toLowerCase()}` : `Ajouter ${title.toLowerCase()}`} onClose={() => setFormOpen(false)}><form onSubmit={submit} className="grid gap-4 sm:grid-cols-2">{fields.map((field) => <label key={field.name} className={`text-sm font-bold text-slate-700 ${field.full ? "sm:col-span-2" : ""}`}>{field.label}{field.type === "textarea" ? <textarea required={field.required} value={values[field.name] ?? ""} onChange={(event) => setValue(field.name, event.target.value)} rows="5" className="mt-1 w-full rounded-lg border p-3 font-normal" /> : field.type === "checkbox" ? <input type="checkbox" checked={Boolean(values[field.name])} onChange={(event) => setValue(field.name, event.target.checked)} className="ml-3" /> : field.options ? <select required={field.required} value={values[field.name] ?? ""} onChange={(event) => setValue(field.name, event.target.value)} className="mt-1 w-full rounded-lg border p-3 font-normal"><option value="">Sélectionner</option>{field.options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : <input type={field.type || "text"} required={field.required} value={field.type === "file" ? undefined : values[field.name] ?? ""} onChange={(event) => setValue(field.name, field.type === "file" ? event.target.files?.[0] : event.target.value)} className="mt-1 w-full rounded-lg border p-3 font-normal" />}</label>)}{mutations.save.isError && <div className="sm:col-span-2"><ErrorMessage error={mutations.save.error} /></div>}<button disabled={mutations.save.isPending} className="sm:col-span-2 rounded-lg bg-haiti-red py-3 font-bold text-white disabled:opacity-50">{mutations.save.isPending ? "Enregistrement…" : "Enregistrer"}</button></form></Modal>}
  </>;
}
