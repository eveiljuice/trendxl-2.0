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
  			// Main color scheme following the monochromatic approach
  			primary: {
  				bg: '#FFFFFF',              // white background
  				card: '#FFFFFF',            // white cards
  				line: '#E5E5E5',            // light borders
  				accent: '#000000',          // black accents
  				'accent-hover': '#666666',   // gray hover state
  				surface: '#F8F8F8',         // secondary light gray background
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			// Text colors for different hierarchy levels
  			text: {
  				primary: '#000000',         // main black text
  				secondary: '#666666',       // subtitle gray
  				placeholder: '#999999'      // placeholder text
  			},
  			// Interactive elements
  			interactive: {
  				bg: '#FFFFFF',              // button background
  				border: '#E5E5E5',          // button border
  				hover: '#F5F5F5',           // button hover
  				text: '#000000'             // button text
  			},
  			// Navigation colors
  			nav: {
  				bg: '#FFFFFF',              // navigation background
  				text: '#000000',            // navigation text
  				hover: '#666666'            // navigation hover
  			},
  			// Content utilities
  			content: {
  				border: '#E0E0E0',          // content borders
  				subtitle: '#666666',        // subtitle text
  				placeholder: '#999999'      // placeholder text
  			},
  			// Tags and categories
  			tags: {
  				bg: '#F0F0F0',              // tag background
  				text: '#666666',            // tag text
  				active: '#000000'           // active tag
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
				card: '16px',               // cards and containers
				btn: '8px',                // buttons
				tag: '9999px',             // tags (fully rounded)
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
			'gradient': 'gradient 8s linear infinite',
			'float': 'float 3s ease-in-out infinite',
			'bounce-subtle': 'bounceSubtle 2s ease-in-out infinite'
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
			},
			float: {
				'0%, 100%': { transform: 'translateY(0px)' },
				'50%': { transform: 'translateY(-10px)' }
			},
			bounceSubtle: {
				'0%, 100%': { transform: 'translateY(0px)' },
				'50%': { transform: 'translateY(-4px)' }
			}
		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
}
