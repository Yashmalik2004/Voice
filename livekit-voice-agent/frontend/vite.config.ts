import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/token': {
        target: 'http://localhost:7880',
        changeOrigin: true,
      },
      '/token': {
        target: 'http://localhost:7880',
        changeOrigin: true,
      },
    },
  },
})
