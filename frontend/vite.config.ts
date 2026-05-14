import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/auth': { target: 'http://localhost:3000', changeOrigin: true },
      '/accounts': { target: 'http://localhost:8080', changeOrigin: true },
      '/transfers': { target: 'http://localhost:8080', changeOrigin: true },
      '/movements': { target: 'http://localhost:8080', changeOrigin: true },
      '/notifications': { target: 'http://localhost:8080', changeOrigin: true },
    },
  },
});
