import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// GODMODE PERFORMANCE OPTIMIZATION
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    allowedHosts: ['3000-ikfm4peco6fgqzbs7q769-2b54fc91.sandbox.novita.ai'],
    host: '0.0.0.0',
    port: 3000,
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
  }
})
