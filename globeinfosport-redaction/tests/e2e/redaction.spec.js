import { test, expect } from "@playwright/test";

async function login(page, account = "e2e-admin") {
  await page.goto("/login");
  await page.getByLabel("Identifiant").fill(account);
  await page.getByLabel("Mot de passe", { exact: true }).fill("BrowserTest!2026");
  await page.getByRole("button", { name: /connecter/i }).click();
  await expect(page.getByRole("heading", { name: /Le terrain inspire/ })).toBeVisible();
}

test("all editorial pages load against the real API", async ({ page }) => {
  test.setTimeout(180000);
  const errors = [];
  page.on("pageerror", error => errors.push(error.message));
  page.on("response", response => {
    if (response.url().includes("/api/") && response.status() >= 400 && !response.url().includes("token/refresh")) errors.push(`${response.status()} ${response.url()}`);
  });
  await login(page);
  for (const path of ["/articles", "/articles/nouveau", "/joueurs", "/championnat/competitions", "/championnat/clubs", "/championnat/selections", "/championnat/clubs/parcours", "/championnat/matchs", "/expatries", "/expatries/clubs", "/expatries/transferts", "/galerie", "/joueurs/legendes", "/sources-externes", "/messages-contact", "/newsletter", "/faq", "/vitrine", "/referentiels", "/comptes"]) {
    await page.goto(path);
    await expect(page.locator("#redaction-contenu h1").first()).toBeVisible();
    await expect(page.getByText("Chargement…", { exact: true })).toHaveCount(0);
    await expect(page.locator('[role="alert"]')).toHaveCount(0);
    if (!["/articles", "/articles/nouveau", "/sources-externes", "/messages-contact", "/newsletter"].includes(path)) {
      await page.getByRole("button", { name: "Ajouter", exact: true }).first().click();
      await expect(page.getByRole("dialog")).toBeVisible();
      await page.getByRole("button", { name: "Annuler", exact: true }).click();
    }
  }
  expect(errors).toEqual([]);
});

test("draft editing, preview, comments and submission preserve text", async ({ page }) => {
  await login(page, "e2e-writer");
  await page.goto("/articles");
  await page.getByRole("link", { name: /Brouillon de test/ }).click();
  await page.getByRole("textbox", { name: "Contenu de l’article" }).fill("Texte conserve apres modification");
  await page.getByRole("button", { name: "Prévisualiser", exact: true }).click();
  await expect(page.locator(".news-preview")).toContainText("Texte conserve apres modification");
  await page.getByRole("button", { name: "Revenir à l’éditeur" }).click();
  await page.getByLabel("Votre commentaire").fill("Commentaire de relecture");
  await page.getByRole("button", { name: "Ajouter un commentaire" }).click();
  await expect(page.getByText("Modifications non enregistrées", { exact: true })).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Contenu de l’article" })).toContainText("Texte conserve apres modification");
  await page.getByRole("button", { name: "Enregistrer", exact: true }).click();
  await expect(page.getByText("Article enregistré.", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Soumettre à la validation" }).click();
  await expect(page.locator(".news-editor-heading")).toContainText("À valider");
  await expect(page.getByRole("button", { name: "Publier maintenant" })).toHaveCount(0);
});

test("reference pagination and role permissions match the API", async ({ page }) => {
  await login(page);
  await page.goto("/championnat/matchs");
  await page.getByRole("button", { name: "Ajouter", exact: true }).click();
  await expect(page.getByLabel("Club domicile").locator("option")).toContainText(["Reference club 104"]);
  await page.getByRole("button", { name: "Annuler", exact: true }).click();
  await page.getByRole("button", { name: "Déconnexion" }).click();
  await login(page, "e2e-writer");
  await page.goto("/championnat/clubs");
  await expect(page.getByRole("heading", { name: "Clubs", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Ajouter", exact: true })).toHaveCount(0);
});

test("accounts use real role ids and accept account creation", async ({ page }) => {
  await login(page);
  await page.goto("/comptes");
  await page.getByRole("button", { name: "Ajouter", exact: true }).click();
  await page.getByLabel("Identifiant").fill("e2e-created");
  await page.getByLabel("Nom", { exact: false }).filter({ hasNot: page.locator('[type="password"]') }).first().fill("Test");
  await page.getByLabel("Rôle").selectOption({ label: "Rédacteur" });
  await page.getByLabel("Mot de passe").fill("ValidAccount!2026");
  await page.getByRole("button", { name: "Enregistrer", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.locator("tbody")).toContainText("e2e-created");
});


test("match results are loaded when reopened", async ({ page }) => {
  await login(page);
  await page.goto("/championnat/matchs");
  await page.getByRole("button", { name: "Saisir le r\u00e9sultat" }).first().click();
  await page.getByLabel("Score domicile").fill("2");
  await page.getByLabel("Score ext\u00e9rieur").fill("1");
  await page.getByRole("button", { name: "Valider le r\u00e9sultat" }).click();
  await expect(page.getByRole("status")).toContainText("enregistr\u00e9");
  await page.reload();
  await expect(page.getByLabel("Score domicile")).toHaveValue("2");
  await expect(page.getByLabel("Score ext\u00e9rieur")).toHaveValue("1");
});

test("mobile navigation opens the newsroom without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page, "e2e-writer");
  await page.getByRole("button", { name: "Ouvrir le menu" }).click();
  await page.getByRole("link", { name: "Articles", exact: true }).last().click();
  await expect(page.getByRole("heading", { name: "Les histoires commencent ici." })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: "test-results/newsroom-mobile.png", fullPage: true });
});
