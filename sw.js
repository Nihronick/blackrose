// BlackRose SW v6 — GitHub Pages /blackrose/
const SHELL_CACHE = 'blackrose-shell-v6'
const API_CACHE = 'blackrose-api-v6'
const BASE = '/blackrose'

const SHELL_ASSETS = [BASE + '/', BASE + '/site.webmanifest']

const API_CACHE_PATTERNS = [
  /\/api\/guide\/[^/]+$/,
  /\/api\/categories$/,
  /\/api\/category\/[^/]+$/,
  /\/api\/top$/,
]

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches
      .open(SHELL_CACHE)
      .then((c) => c.addAll(SHELL_ASSETS).catch(() => {}))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', (e) => {
  const KEEP = [SHELL_CACHE, API_CACHE]
  e.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => !KEEP.includes(k)).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', (e) => {
  const { request } = e
  const url = new URL(request.url)
  if (request.method !== 'GET') return
  if (url.hostname === 'telegram.org') return

  const isApiCacheable = API_CACHE_PATTERNS.some((p) => p.test(url.pathname))
  if (isApiCacheable) {
    e.respondWith(
      fetch(request)
        .then((res) => {
          if (res.ok) {
            try {
              const copy = res.clone()
              caches
                .open(API_CACHE)
                .then((c) => c.put(request, copy))
                .catch(() => {})
            } catch {}
          }
          return res
        })
        .catch(() => caches.match(request))
    )
    return
  }

  if (
    url.origin === self.location.origin &&
    url.pathname.startsWith(BASE) &&
    /(\.(js|css|png|svg|ico|webp|gif|woff2?)$|\/$)/.test(url.pathname)
  ) {
    e.respondWith(
      caches.open(SHELL_CACHE).then((cache) =>
        cache.match(request).then((cached) => {
          const net = fetch(request)
            .then((res) => {
              if (res.ok) {
                try {
                  const copy = res.clone()
                  cache.put(request, copy).catch(() => {})
                } catch {}
              }
              return res
            })
            .catch(() => cached || Response.error())
          return cached || net
        })
      )
    )
  }
})

self.addEventListener('push', (e) => {
  if (!e.data) return
  try {
    const data = e.data.json()
    e.waitUntil(
      self.registration.showNotification(data.title || 'BlackRose', {
        body: data.body || '',
        icon: BASE + '/web-app-manifest-192x192.png',
        badge: BASE + '/favicon-96x96.png',
        data: { url: data.url || BASE + '/' },
        vibrate: [100, 50, 100],
      })
    )
  } catch {}
})

self.addEventListener('notificationclick', (e) => {
  e.notification.close()
  const url = e.notification.data?.url || BASE + '/'
  e.waitUntil(
    clients.matchAll({ type: 'window' }).then((list) => {
      for (const c of list) {
        if (c.url.includes(self.location.origin) && 'focus' in c) {
          c.navigate(url)
          return c.focus()
        }
      }
      return clients.openWindow(url)
    })
  )
})
