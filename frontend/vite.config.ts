import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Forward API calls to the FastAPI backend so the browser sees same-origin
    // requests (no CORS needed in dev). `/api/...` -> http://localhost:8000/api/...
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
})
