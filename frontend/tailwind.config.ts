import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/app/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Marque : indigo → violet
        primary: {
          DEFAULT: "#6366f1",
          dark: "#4f46e5",
          foreground: "#ffffff",
        },
        brand: {
          50: "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(99,102,241,0.45)",
        card: "0 1px 2px 0 rgba(16,24,40,0.05), 0 1px 3px 0 rgba(16,24,40,0.08)",
        "card-hover": "0 10px 30px -10px rgba(16,24,40,0.18)",
      },
      backgroundImage: {
        "grid-light":
          "linear-gradient(to right, rgba(99,102,241,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(99,102,241,0.08) 1px, transparent 1px)",
      },
      keyframes: {
        aurora: {
          "0%": { backgroundPosition: "50% 50%, 50% 50%" },
          "50%": { backgroundPosition: "100% 0%, 0% 100%" },
          "100%": { backgroundPosition: "50% 50%, 50% 50%" },
        },
        "gradient-x": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        shimmer: {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(100%)" },
        },
        "border-beam": {
          "100%": { "offset-distance": "100%" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.8)", opacity: "0.6" },
          "100%": { transform: "scale(2.2)", opacity: "0" },
        },
      },
      animation: {
        aurora: "aurora 18s ease-in-out infinite",
        "gradient-x": "gradient-x 6s ease infinite",
        shimmer: "shimmer 2.5s infinite",
        "border-beam": "border-beam calc(var(--duration,8)*1s) infinite linear",
        "fade-up": "fade-up 0.6s cubic-bezier(0.16,1,0.3,1) both",
        float: "float 6s ease-in-out infinite",
        "pulse-ring": "pulse-ring 2.4s cubic-bezier(0.4,0,0.6,1) infinite",
      },
    },
  },
  plugins: [],
};

export default config;
