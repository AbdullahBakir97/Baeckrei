/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3B82F6', // Blue-500
          dark: '#2563EB',    // Blue-600
          light: '#60A5FA',   // Blue-400
        },
        secondary: {
          DEFAULT: '#10B981', // Emerald-500
          dark: '#059669',    // Emerald-600
          light: '#34D399',   // Emerald-400
        },
        accent: {
          DEFAULT: '#8B5CF6', // Violet-500
          dark: '#7C3AED',    // Violet-600
          light: '#A78BFA',   // Violet-400
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
    require("@aksharahegde/vue-glow/tailwind")
  ],
}
