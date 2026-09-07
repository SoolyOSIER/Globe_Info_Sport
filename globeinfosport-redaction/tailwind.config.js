/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        haiti: { blue: "#00209f", red: "#d21034", ink: "#0f172a" },
      },
      boxShadow: { panel: "0 14px 32px rgba(15, 23, 42, .09)" },
    },
  },
  plugins: [],
};
