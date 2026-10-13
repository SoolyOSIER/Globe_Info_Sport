import assert from "node:assert/strict";
import { test } from "node:test";
import { initialValues, prepareValues } from "../src/utils/resourceForms.js";

test("a match date can be edited without changing its instant", () => {
  const fields = [{ name: "date_heure", type: "datetime-local" }];
  const value = "2026-09-22T19:30:00Z";
  const initial = initialValues(fields, { date_heure: value });
  assert.match(initial.date_heure, /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/);
  assert.equal(prepareValues(fields, initial).date_heure, new Date(value).toISOString());
});

test("uploading a logo preserves empty lists and false values", () => {
  const fields = [{ name: "logo", type: "file" }, { name: "clubs", multiple: true }, { name: "actif", type: "checkbox" }];
  const file = new File(["test"], "logo.png", { type: "image/png" });
  const result = prepareValues(fields, { logo: file, clubs: [], actif: false });
  assert.ok(result instanceof FormData);
  assert.deepEqual(JSON.parse(result.get("payload")), { clubs: [], actif: false });
  assert.equal(result.get("logo").name, "logo.png");
});

test("an unchanged image and blank password are preserved", () => {
  const fields = [{ name: "photo", type: "file" }, { name: "password", type: "password" }, { name: "nom" }];
  assert.deepEqual(prepareValues(fields, { photo: "/media/photo.png", password: "", nom: "Updated" }, true), { nom: "Updated" });
});

test("related objects and optional fields survive editing", () => {
  const fields = [{ name: "sport", options: [] }, { name: "clubs", multiple: true }, { name: "actif", type: "checkbox", defaultValue: true }];
  assert.deepEqual(initialValues(fields, { sport: { id: 12 }, clubs: [1, { id: 2 }], actif: false }), { sport: 12, clubs: ["1", "2"], actif: false });
  assert.deepEqual(prepareValues(fields, { sport: "", clubs: [], actif: false }, true), { sport: null, clubs: [], actif: false });
});
