/* FIN.AI — Service Worker v2 */

const CACHE_NAME = 'finai-v2';

/* Ressources statiques mises en cache dès l'installation */
const PRECACHE = [
  '/static/css/finai.css',
  '/static/css/pwa.css',
  '/static/js/finai.js',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/offline/',
];

/* ── Installation : précache les ressources statiques ── */
self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE))
  );
});

/* ── Activation : supprime les anciens caches ── */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

/* ── Fetch : stratégie Network-first avec fallback cache ── */
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  /* Ne pas intercepter les requêtes non-GET ou cross-origin */
  if (request.method !== 'GET' || url.origin !== location.origin) return;

  /* Ressources statiques → Cache-first */
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          return response;
        });
      })
    );
    return;
  }

  /* Pages HTML → Network-first, fallback offline */
  event.respondWith(
    fetch(request)
      .then(response => {
        /* Met en cache les pages réussies */
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        }
        return response;
      })
      .catch(() =>
        caches.match(request).then(cached =>
          cached || caches.match('/offline/')
        )
      )
  );
});

/* ── Push Notifications ── */
self.addEventListener('push', event => {
  let data = { title: 'FIN.AI', body: 'Nouvelle alerte financière', url: '/dashboard/' };
  try { data = { ...data, ...event.data.json() }; } catch (e) {}
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body:    data.body,
      icon:    '/static/icons/icon-192.png',
      badge:   '/static/icons/icon-192.png',
      tag:     'finai-alert',
      renotify: true,
      data:    { url: data.url },
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = event.notification.data?.url || '/dashboard/';
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(all => {
      for (const c of all) {
        if (c.url === url && 'focus' in c) return c.focus();
      }
      return clients.openWindow(url);
    })
  );
});
