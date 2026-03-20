const CACHE_NAME = 'blackrose-v1'
const GUIDE_CACHE = 'blackrose-guides-v1'
const STATIC_ASSETS = ['/', '/index.html']

// Guides to cache on read (read-through cache)
const API_CACHE_PATTERNS = [
  /\/api\/guide\/[^/]+$/,
  /\/api\/categories$/,
  /\/api\/category\/[^/]+$/,
]

self.addEventListener('install', e => {
  self.skipWaiting()
  e.waitUntil(
    caches.open(CACHE_NAME).then(c => c.addAll(STATIC_ASSETS).catch(() => {}))
  )
})

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys
        .filter(k => k !== CACHE_NAME && k !== GUIDE_CACHE)
        .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', e => {
  const { request } = e
  const url = new URL(request.url)

  // Only handle GET
  if (request.method !== 'GET') return

  // API guide caching (network-first, fallback to cache)
  const isApiCacheable = API_CACHE_PATTERNS.some(p => p.test(url.pathname))
  if (isApiCacheable) {
    e.respondWith(
      fetch(request)
        .then(res => {
          if (res.ok) {
            const clone = res.clone()
            caches.open(GUIDE_CACHE).then(c => c.put(request, clone))
          }
          return res
        })
        .catch(() => caches.match(request))
    )
    return
  }

  // Static assets: cache-first
  if (url.origin === self.location.origin) {
    e.respondWith(
      caches.match(request).then(cached => cached || fetch(request))
    )
  }
})
