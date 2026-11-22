import { defineConfig } from 'vite';
// base './' so the built site works from any folder / static server
export default defineConfig({ base: './', build: { target: 'es2022', chunkSizeWarningLimit: 3000 }, server: { port: 5173, open: true } });
