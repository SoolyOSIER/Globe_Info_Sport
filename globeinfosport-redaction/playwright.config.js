import { resolve } from "node:path";
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  timeout: 45000,
  use: {
    baseURL: "http://127.0.0.1:5177",
    browserName: "chromium",
    channel: process.env.PLAYWRIGHT_CHANNEL || "msedge",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command: `"${resolve("../globeinfosport-backend/.venv312/Scripts/python.exe")}" "${resolve("../scripts/e2e-api.py")}"`,
      url: "http://127.0.0.1:8011/api/v1/public/sports/",
      timeout: 120000,
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 5177",
      url: "http://127.0.0.1:5177",
      env: { API_PROXY_TARGET: "http://127.0.0.1:8011", VITE_API_URL: "/api/v1" },
      reuseExistingServer: false,
    },
  ],
});
