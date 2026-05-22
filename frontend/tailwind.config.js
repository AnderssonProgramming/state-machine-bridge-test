/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#2A3759",
        brand: "#3556AC",
        bright: "#3A64D1",
        lila: "#A0AAF9",
        peach: "#FD8266",
        fucsia: "#FF5180",
        lime: "#A9FF62",
      },
    },
  },
  plugins: [],
};