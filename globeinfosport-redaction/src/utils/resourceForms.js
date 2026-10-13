export function localDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

export function initialValues(fields, record) {
  return Object.fromEntries(fields.map(field => {
    const raw = record?.[field.name];
    let value = raw && typeof raw === "object" && "id" in raw ? raw.id : raw;
    if (field.multiple && Array.isArray(raw)) value = raw.map(item => String(item?.id ?? item));
    if (field.type === "datetime-local") value = localDateTime(raw);
    return [field.name, value ?? field.defaultValue ?? (field.type === "checkbox" ? false : field.multiple ? [] : "")];
  }));
}

export function prepareValues(fields, values, editing = false) {
  const payload = {};
  const files = [];
  for (const field of fields) {
    if (field.readOnly) continue;
    let value = values[field.name];
    if (field.type === "file") {
      if (value instanceof File) files.push([field.name, value]);
      continue;
    }
    if (field.type === "password" && !value) continue;
    if (field.type === "checkbox") value = Boolean(value);
    if (value === "" && (field.options || ["number", "date", "datetime-local"].includes(field.type))) {
      if (editing) payload[field.name] = null;
      continue;
    }
    if (field.type === "datetime-local" && value) value = new Date(value).toISOString();
    if (value !== undefined) payload[field.name] = value;
  }
  if (!files.length) return payload;
  const body = new FormData();
  body.append("payload", JSON.stringify(payload));
  for (const [name, file] of files) body.append(name, file);
  return body;
}
