/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette from design
        navy: {
          50: '#F2F4F6',
          100: '#E6EBEF',
          200: '#BFCDD8',
          300: '#99AFB9',
          400: '#6F8596',
          500: '#2F4156',
          600: '#27364A',
          700: '#1F2738',
          800: '#161A24',
          900: '#0B0D12',
        },
        teal: {
          50: '#F6F8F9',
          100: '#EEF3F5',
          200: '#BCDDE3',
          300: '#92C6CF',
          400: '#69AEBF',
          500: '#567C8D',
          600: '#466670',
          700: '#354C53',
          800: '#223334',
          900: '#10191A',
        },
        beige: {
          50: '#FBF9F7',
          100: '#F7F3F0',
          200: '#F1EDE8',
          300: '#ECE6E0',
          400: '#F5EFE8',
          500: '#F5EFE8',
          600: '#D9D1C9',
          700: '#BFB6AB',
          800: '#9F9589',
          900: '#7C7366',
        },
        sky: {
          50: '#F7F9FB',
          100: '#EDF4F8',
          200: '#C8D9E6',
          300: '#A8C8DB',
          400: '#86B6CF',
          500: '#C8D9E6',
          600: '#9FBFD0',
          700: '#6F99B0',
          800: '#4B768E',
          900: '#314E63',
        },
        brandWhite: '#FFFFFF',

        // Keep existing primary/secondary keys but map them to brand shades
        primary: {
          50: '#F2F4F6',
          100: '#E6EBEF',
          200: '#BFCDD8',
          300: '#99AFB9',
          400: '#6F8596',
          500: '#2F4156',
          600: '#27364A',
          700: '#1F2738',
          800: '#161A24',
          900: '#0B0D12',
        },
        secondary: {
          50: '#F6F8F9',
          100: '#EEF3F5',
          200: '#BCDDE3',
          300: '#92C6CF',
          400: '#69AEBF',
          500: '#567C8D',
          600: '#466670',
          700: '#354C53',
          800: '#223334',
          900: '#10191A',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}