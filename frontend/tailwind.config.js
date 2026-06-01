/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#030712',      // Deep space black
          card: 'rgba(17, 24, 39, 0.7)', // Sleek glass card
          copper: '#f97316',    // PCB copper track neon orange
          copperglow: 'rgba(249, 115, 22, 0.15)',
          cyan: '#06b6d4',      // Hardware tracer neon cyan
          green: '#10b981',     // PCB soldermask emerald green
          gold: '#fbbf24',      // Test point ENIG gold
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Outfit', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        'glow-copper': '0 0 15px rgba(249, 115, 22, 0.45)',
        'glow-cyan': '0 0 15px rgba(6, 182, 212, 0.45)',
        'glow-green': '0 0 15px rgba(16, 185, 129, 0.35)',
      },
      backgroundImage: {
        'grid-pattern': "radial-gradient(rgba(249, 115, 22, 0.08) 1px, transparent 0)",
      }
    },
  },
  plugins: [],
}
