import { ChakraProvider, createSystem, defaultConfig, defineConfig } from '@chakra-ui/react'
import { ReactNode } from 'react'

const config = defineConfig({
  theme: {
    tokens: {
      colors: {
        primary: {
          bg: { value: '#0B0B0F' },
          card: { value: '#1A1A1F' },
          line: { value: '#2A2A30' },
          accent: { value: '#0000ff' },
          'accent-hover': { value: '#2F6FFF' },
        },
        text: {
          primary: { value: '#FFFFFF' },
          secondary: { value: '#A1A1AA' }
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
