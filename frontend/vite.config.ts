import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// In development the API runs on uvicorn's default port; in production FastAPI serves
// the built files itself, so the browser only ever talks to one origin.
const api = 'http://127.0.0.1:8000'
const apiPaths = ['/chat', '/conversations', '/reports', '/results', '/health']

export default defineConfig({
  plugins: [react()],
  server: { proxy: Object.fromEntries(apiPaths.map((path) => [path, api])) },
})
