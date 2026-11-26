import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { defineConfig, type Plugin } from 'vite';

const root = path.dirname(fileURLToPath(import.meta.url));
const pub = path.join(root, 'public');

/** Vite SPA fallback steals /docs/…/ and /library/…/ — map those to public/.../index.html (Zensical sites). */
function serveStaticSiteIndexes(prefixes: string[]): Plugin {
  const rewrite = (req: { url?: string }, _res: unknown, next: () => void) => {
    const raw = req.url || '';
    const q = raw.indexOf('?');
    const pathname = (q >= 0 ? raw.slice(0, q) : raw).split('#')[0];
    const search = q >= 0 ? raw.slice(q) : '';
    const prefix = prefixes.find((p) => pathname === p || pathname.startsWith(`${p}/`));
    if (!prefix) return next();

    let dir = pathname;
    if (dir === prefix) dir = `${prefix}/`;
    if (!dir.endsWith('/') && !path.extname(dir)) dir += '/';
    if (!dir.endsWith('/')) return next();

    const indexFile = path.join(pub, dir.slice(1), 'index.html');
    if (fs.existsSync(indexFile)) req.url = `${dir}index.html${search}`;
    next();
  };

  return {
    name: 'serve-static-site-indexes',
    configureServer(s) { s.middlewares.use(rewrite); },
    configurePreviewServer(s) { s.middlewares.use(rewrite); },
  };
}

// base './' so the built site works from any folder / static server
export default defineConfig({
  base: './',
  plugins: [serveStaticSiteIndexes(['/docs', '/library'])],
  build: { target: 'es2022', chunkSizeWarningLimit: 3000 },
  server: { port: 5173, open: true },
});
