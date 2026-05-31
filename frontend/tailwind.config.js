/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: "var(--color-brand)",
        "brand-fg": "var(--color-brand-fg)",
      },
    },
  },
  plugins: [],
};
