import { defineConfig } from 'vite';

export default defineConfig({
  root: 'frontend',
  server: {
    port: 5173
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true
  }
});