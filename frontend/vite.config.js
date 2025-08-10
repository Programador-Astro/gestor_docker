import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,       // Permite acesso externo (útil no Docker)
    port: 5173, // Porta padrão do Vite
    watch: {
      usePolling: true
    }              
  },
  build: {
    outDir: 'dist',        // Garantia do nome da pasta de build
  }
})
