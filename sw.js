// Offline cache.
//  shell + course data: versioned, network-first so new units appear; replaced on each release.
//  audio (data/voice/*.mp3, native recordings) and CDN libraries/fonts/stroke data: content never changes for a URL,
//  so cache-first in caches that survive releases. Audio is capped (oldest dropped first) so the phone never fills up.
const V = 'zhangda-v36';
const AUDIO = 'zhangda-audio', CDN = 'zhangda-cdn', AUDIO_MAX = 2500; // ~25 MB of clips
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon.svg', 'data/index.json', 'data/syllables.json', 'data/radicals.json'];
self.addEventListener('install', e => e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => ![V, AUDIO, CDN].includes(k)).map(k => caches.delete(k)))).then(() => self.clients.claim())));
let trimming = null;
function trimAudio(c) { // drop the oldest clips past the cap (cache keys keep insertion order)
  if (trimming) return trimming;
  return trimming = c.keys().then(ks => Promise.all(ks.slice(0, Math.max(0, ks.length - AUDIO_MAX)).map(k => c.delete(k)))).finally(() => { trimming = null; });
}
function cacheFirst(e, name, cap) {
  e.respondWith(caches.open(name).then(c => c.match(e.request).then(hit => hit || fetch(e.request).then(res => {
    if (res.ok) c.put(e.request, res.clone()).then(() => cap && trimAudio(c));
    return res;
  }))));
}
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  const audio = /\.(mp3|ogg|m4a)$/.test(u.pathname);
  if (u.origin === location.origin && audio) return cacheFirst(e, AUDIO, true);
  if (['cdn.jsdelivr.net', 'fonts.googleapis.com', 'fonts.gstatic.com', 'api.fontshare.com', 'cdn.fontshare.com'].includes(u.hostname)) return cacheFirst(e, audio ? AUDIO : CDN, audio);
  if (u.origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(res => { if (res.ok) { const cl = res.clone(); caches.open(V).then(c => c.put(e.request, cl)); } return res; }).catch(() => caches.match(e.request, { ignoreSearch: true })));
});
