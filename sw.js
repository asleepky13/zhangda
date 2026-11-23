// Offline cache: app shell + course data (network-first so new units appear), CDN stroke data (cache-first).
const V = 'zhangda-v13';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon.svg', 'data/index.json', 'data/syllables.json'];
self.addEventListener('install', e => e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  if (['cdn.jsdelivr.net', 'fonts.googleapis.com', 'fonts.gstatic.com', 'api.fontshare.com', 'cdn.fontshare.com'].includes(u.hostname)) {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(res => { if (res.ok) caches.open(V).then(c => c.put(e.request, res.clone())); return res; })));
    return;
  }
  if (u.origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(res => { if (res.ok) { const cl = res.clone(); caches.open(V).then(c => c.put(e.request, cl)); } return res; }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
