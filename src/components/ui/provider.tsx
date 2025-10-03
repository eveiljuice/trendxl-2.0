import { ChakraProvider, createSystem, defaultConfig, defineConfig } from '@chakra-ui/react'
import { ReactNode } from 'react'

const config = defineConfig({
  theme: {
    tokens: {
      colors: {
        // Main color scheme following monochromatic approach
        primary: {
          bg: { value: '#FFFFFF' },         // white background
          card: { value: '#FFFFFF' },       // white cards
          line: { value: '#E5E5E5' },       // light borders
          accent: { value: '#000000' },     // black accents
          'accent-hover': { value: '#666666' }, // gray hover
        },
        // Text hierarchy
        text: {
          primary: { value: '#000000' },    // main black text
          secondary: { value: '#666666' }   // secondary gray text
        },
        // Interactive elements
        interactive: {
          bg: { value: '#FFFFFF' },         // button background
          border: { value: '#E5E5E5' },     // button border
          hover: { value: '#F5F5F5' },      // button hover
          text: { value: '#000000' }        // button text
        },
        // Navigation
        nav: {
          bg: { value: '#FFFFFF' },         // nav background
          text: { value: '#000000' },       // nav text
          hover: { value: '#666666' }       // nav hover
        },
        // Content utilities
        content: {
          border: { value: '#E0E0E0' },     // content borders
          subtitle: { value: '#666666' },   // subtitle text
          placeholder: { value: '#999999' } // placeholder text
        },
        // Tags
        tags: {
          bg: { value: '#F0F0F0' },         // tag background
          text: { value: '#666666' },       // tag text
          active: { value: '#000000' }      // active tag
        }
      },
      fonts: {
        heading: { value: "'Orbitron', monospace" },
        body: { value: "'Inter', system-ui, sans-serif" },
        mono: { value: "'JetBrains Mono', monospace" },
      }
    }
  }
})

const system = createSystem(defaultConfig, config)

interface ProviderProps {
  children: ReactNode
}

export function Provider({ children }: ProviderProps) {
  return (
    <ChakraProvider value={system}>
      {children}
    </ChakraProvider>
  )
}
