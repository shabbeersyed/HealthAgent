import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // ✅ Ensures all paths work correctly on Vercel (SPA routing)
  build: {
    outDir: 'dist', // ✅ Vercel serves from this folder
  },
  server: {
    port: 5500,
    watch: {
      ignored: [
        '**/backend/**',
        '**/backend/Project_7_HealthAgent/**',
        '**/backend/Project_7_HealthAgent/generated/**',
        '**/generated/**',
        '**/*.pdf',
        '**/*.wav',
        '**/*.mp3'
      ]
    }
  }
})
