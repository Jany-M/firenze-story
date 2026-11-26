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

/** Hot reload for generated assets: when the pipeline or Blender rewrites models, data, textures or materials in public/,
 *  open pages reload once the writes settle (Vite does not reload for public/ edits on its own). */
function reloadOnAssets(dirs: string[]): Plugin {
  return {
    name: 'reload-on-assets',
    configureServer(s) {
      const roots = dirs.map(d => path.join(pub, d));
      s.watcher.add(roots);
      let t: ReturnType<typeof setTimeout> | null = null; const changed = new Set<string>();
      const hit = (f: string) => {
        if (!roots.some(r => f.startsWith(r))) return;
        changed.add(path.relative(pub, f)); if (t) clearTimeout(t);
        t = setTimeout(() => { s.config.logger.info(`assets changed (${[...changed].slice(0, 3).join(', ')}${changed.size > 3 ? ', …' : ''}), reloading`, { timestamp: true });
          changed.clear(); s.ws.send({ type: 'full-reload', path: '*' }); }, 800);
      };
      s.watcher.on('change', hit); s.watcher.on('add', hit); s.watcher.on('unlink', hit);
    },
  };
}

// base './' so the built site works from any folder / static server
export default defineConfig({
  base: './',
  plugins: [serveStaticSiteIndexes(['/docs', '/library']), reloadOnAssets(['models', 'data', 'textures', 'materials'])],
  build: { target: 'es2022', chunkSizeWarningLimit: 3000 },
  server: { port: 5173, open: true },
});
