/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fef5ee',
          100: '#fde9d7',
          200: '#fbcfae',
          300: '#f8af7a',
          400: '#f48544',
          500: '#f16420',
          600: '#e24a16',
          700: '#bb3614',
          800: '#952d18',
          900: '#782716',
        },
      },
    },
  },
  plugins: [],
}
