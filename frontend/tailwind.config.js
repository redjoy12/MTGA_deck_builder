/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'mtga-blue': '#1a237e',
        'mtga-gold': '#ffd700',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

