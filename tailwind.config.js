/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'inter': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        // Apple минималистичная цветовая схема
        primary: {
          bg: '#0B0B0F',      // Основной фон
          card: '#1A1A1F',    // Карточки
          line: '#2A2A30',    // Линии/границы
          accent: '#0000ff',  // Акцентный синий
          'accent-hover': '#2F6FFF', // Акцент при наведении
        },
        text: {
          primary: '#FFFFFF',   // Основной текст
          secondary: '#A1A1AA', // Вторичный текст
        }
      },
      spacing: {
        '16': '64px',  // Отступы между секциями
        '6': '24px',   // Отступы между элементами
      },
      borderRadius: {
        'card': '16px',  // Радиус карточек
        'btn': '8px',    // Радиус кнопок
      },
      boxShadow: {
        'accent': '0 0 8px rgba(58, 124, 255, 0.3)', // Тень для кнопок при наведении
      },
      animation: {
        'fade-in': 'fadeIn 300ms ease-out',
        'slide-up': 'slideUp 400ms ease-out',
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [],
}
