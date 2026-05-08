export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        midnight: "#0f172a",
        slateBlue: "#111a35",
        electric: "#6366f1",
        sunset: "#fb7185",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 25px 50px rgba(15, 23, 42, 0.15)",
        glow: "0 15px 40px rgba(99, 102, 241, 0.25)",
      },
    },
  },
  plugins: [],
};
