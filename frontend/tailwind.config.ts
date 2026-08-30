/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          500: "#3b64f0",
          600: "#2f4fd6",
          700: "#273fb0",
        },
        risk: {
          low: "#16a34a",
          medium: "#ca8a04",
          high: "#dc2626",
        },
      },
    },
  },
  plugins: [],
};
