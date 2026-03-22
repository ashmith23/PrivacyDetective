/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        appleBlue: '#0071E3',
        appleRed: '#FF3B30',
        appleGray: '#F5F5F7',
      },
    },
  },
  plugins: [],
}