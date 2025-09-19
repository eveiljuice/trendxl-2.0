/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ["class"],
    content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
  	extend: {
		fontFamily: {
			inter: [
				'Inter',
				'system-ui',
				'-apple-system',
				'sans-serif'
			],
			orbitron: [
				'Orbitron',
				'monospace'
			],
			jetbrains: [
				'JetBrains Mono',
				'monospace'
			]
		},
  		colors: {
  			primary: {
  				bg: '#0B0B0F',
  				card: '#1A1A1F',
  				line: '#2A2A30',
  				accent: '#0000ff',
  				'accent-hover': '#2F6FFF',
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			text: {
  				primary: '#FFFFFF',
  				secondary: '#A1A1AA'
  			},
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		spacing: {
  			'6': '24px',
  			'16': '64px'
  		},
  		borderRadius: {
  			card: '16px',
  			btn: '8px',
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		boxShadow: {
  			accent: '0 0 8px rgba(58, 124, 255, 0.3)'
  		},
		animation: {
			'fade-in': 'fadeIn 300ms ease-out',
			'slide-up': 'slideUp 400ms ease-out',
			'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
			'gradient': 'gradient 8s linear infinite'
		},
		keyframes: {
			fadeIn: {
				'0%': {
					opacity: '0',
					transform: 'translateY(10px)'
				},
				'100%': {
					opacity: '1',
					transform: 'translateY(0)'
				}
			},
			slideUp: {
				'0%': {
					opacity: '0',
					transform: 'translateY(20px)'
				},
				'100%': {
					opacity: '1',
					transform: 'translateY(0)'
				}
			},
			gradient: {
				'0%': { backgroundPosition: '0% 50%' },
				'50%': { backgroundPosition: '100% 50%' },
				'100%': { backgroundPosition: '0% 50%' }
			}
		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
}
