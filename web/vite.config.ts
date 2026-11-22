import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig, type Plugin } from 'vite';

const root = path.dirname(fileURLToPath(import.meta.url));
const pub = path.join(root, 'public');

/** Vite SPA fallback steals /docs/…/ — map those to public/docs/.../index.html (Zensical site). */
function serveDocsIndexes(): Plugin {
  const rewrite = (req: { url?: string }, _res: unknown, next: () => void) => {
    const raw = req.url || '';
    const q = raw.indexOf('?');
    const pathname = (q >= 0 ? raw.slice(0, q) : raw).split('#')[0];
    const search = q >= 0 ? raw.slice(q) : '';
    if (!pathname.startsWith('/docs')) return next();

    let dir = pathname;
    if (dir === '/docs') dir = '/docs/';
    if (!dir.endsWith('/') && !path.extname(dir)) dir += '/';
    if (!dir.endsWith('/')) return next();

    const indexFile = path.join(pub, dir.slice(1), 'index.html');
    if (fs.existsSync(indexFile)) req.url = `${dir}index.html${search}`;
    next();
  };

  return {
    name: 'serve-docs-indexes',
    configureServer(s) { s.middlewares.use(rewrite); },
    configurePreviewServer(s) { s.middlewares.use(rewrite); },
  };
}

// base './' so the built site works from any folder / static server
export default defineConfig({
  base: './',
  plugins: [serveDocsIndexes()],
  build: { target: 'es2022', chunkSizeWarningLimit: 3000 },
  server: { port: 5173, open: true },
});
