import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#111111",
        mist: "#f5f1e8",
        sand: "#d9c9ab",
        accent: "#1f6f5f",
        ember: "#b55233"
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui"],
        serif: ["var(--font-serif)", "ui-serif", "Georgia"]
      },
      boxShadow: {
        panel: "0 24px 80px rgba(17, 17, 17, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;

