/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Backlover palette: a bakery at night, lit by the oven.
        oven: {
          950: '#0e0c0a', // page
          900: '#15120f', // surface
          800: '#1e1914', // raised surface
          700: '#2a231c', // borders on dark
        },
        cream: {
          DEFAULT: '#f4ece1',
          muted: '#b9ab98',
          faint: '#7d7061',
        },
        crust: {
          DEFAULT: '#e6a15a', // golden caramel accent
          light: '#f2c48d',
          dark: '#b8733a',
        },
        ember: '#d2603f',
        primary: {
          DEFAULT: '#3B82F6',
          dark: '#2563EB',
          light: '#60A5FA',
        },
        secondary: {
          DEFAULT: '#10B981',
          dark: '#059669',
          light: '#34D399',
        },
        accent: {
          DEFAULT: '#8B5CF6',
          dark: '#7C3AED',
          light: '#A78BFA',
        }
      },
      fontFamily: {
        sans: ['"Manrope Variable"', 'Manrope', 'system-ui', 'sans-serif'],
        display: ['"Instrument Serif"', 'Georgia', 'serif'],
      },
      letterSpacing: {
        tightest: '-0.04em',
      },
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
    require("@aksharahegde/vue-glow/tailwind")
  ],
}
