/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a16', // Keeping fallback, but clay uses #F4F1FA
        clay: {
          canvas: '#F4F1FA',
          foreground: '#332F3A',
          muted: '#635F69',
          cardBg: 'rgba(255, 255, 255, 0.65)',
          accent: {
            DEFAULT: '#7C3AED', // Violet
            hover: '#6D28D9',
            secondary: '#DB2777', // Hot Pink
            tertiary: '#0EA5E9', // Sky Blue
            success: '#10B981',
            warning: '#F59E0B',
          }
        }
      },
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        display: ['Nunito', 'sans-serif'],
      },
      borderRadius: {
        '4xl': '32px',
        '5xl': '48px',
        '6xl': '60px',
      },
      boxShadow: {
        clayCard: '16px 16px 32px rgba(160, 150, 180, 0.2), -10px -10px 24px rgba(255, 255, 255, 0.9), inset 6px 6px 12px rgba(139, 92, 246, 0.03), inset -6px -6px 12px rgba(255, 255, 255, 1)',
        clayButton: '12px 12px 24px rgba(139, 92, 246, 0.3), -8px -8px 16px rgba(255, 255, 255, 0.4), inset 4px 4px 8px rgba(255, 255, 255, 0.4), inset -4px -4px 8px rgba(0, 0, 0, 0.1)',
        clayButtonHover: '16px 16px 32px rgba(139, 92, 246, 0.4), -8px -8px 16px rgba(255, 255, 255, 0.4), inset 4px 4px 8px rgba(255, 255, 255, 0.4), inset -4px -4px 8px rgba(0, 0, 0, 0.1)',
        clayPressed: 'inset 10px 10px 20px #d9d4e3, inset -10px -10px 20px #ffffff',
        deepClay: '30px 30px 60px #cdc6d9, -30px -30px 60px #ffffff, inset 10px 10px 20px rgba(139, 92, 246, 0.05), inset -10px -10px 20px rgba(255, 255, 255, 0.8)',
      },
      animation: {
        'clay-float': 'clay-float 8s ease-in-out infinite',
        'clay-float-delayed': 'clay-float-delayed 10s ease-in-out infinite',
        'clay-float-slow': 'clay-float-slow 12s ease-in-out infinite',
        'clay-breathe': 'clay-breathe 6s ease-in-out infinite',
      },
      keyframes: {
        'clay-float': {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '50%': { transform: 'translateY(-20px) rotate(2deg)' },
        },
        'clay-float-delayed': {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '50%': { transform: 'translateY(-15px) rotate(-2deg)' },
        },
        'clay-float-slow': {
          '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
          '50%': { transform: 'translateY(-30px) rotate(5deg)' },
        },
        'clay-breathe': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.02)' },
        }
      }
    },
  },
  plugins: [],
}
