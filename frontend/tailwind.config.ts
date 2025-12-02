import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        enhanced: {
          bg: "#f6f8fc",
          card: "#ffffff",
          border: "#dfe1e5",
          text: "#1f1f1f",
          accent: "#5865f2"
        }
      },
      fontFamily: {
        display: ["'Press Start 2P'", "cursive"],
        sans: ["'Google Sans'", "Inter", "system-ui", "sans-serif"]
      },
      boxShadow: {
        floating: "0 20px 60px rgba(15,23,42,0.12)"
      }
    }
  },
  plugins: []
};

export default config;

