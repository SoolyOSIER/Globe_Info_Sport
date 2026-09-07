/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        haiti: { blue: "#00209f", red: "#d21034", gold: "#f6c945", ink: "#102044" },
      },
      fontFamily: { display: ["Montserrat", "ui-sans-serif", "system-ui"], body: ["Inter", "ui-sans-serif", "system-ui"] },
      boxShadow: { card: "0 14px 40px rgba(16, 32, 68, .12)" },
    },
  },
  plugins: [],
};
