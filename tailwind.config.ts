import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        retro: {
          orange: "#FF5722",
          orangeHover: "#FF7043",
          orangeLight: "#FFAB91",
          amber: "#FFB300",
          yellow: "#FFD54F",
          darkBg: "#0a0a0c",
          darkSurface: "#121217",
          darkBorder: "#272733",
          darkCard: "#16161d",
          lightBg: "#f8f9fc",
          lightSurface: "#ffffff",
          lightBorder: "#e2e8f0",
          lightCard: "#f1f5f9",
          green: "#00E676",
          cyan: "#00E5FF",
          purple: "#B388FF",
        },
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        pixel: ['"Press Start 2P"', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'pixel-orange': '4px 4px 0px 0px #FF5722',
        'pixel-dark': '4px 4px 0px 0px #000000',
        'pixel-glow': '0 0 15px rgba(255, 87, 34, 0.4)',
      },
    },
  },
  plugins: [],
};

export default config;
