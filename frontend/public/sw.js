// BlackRose SW v3 — только API кеш, статика всегда с сервера
const CACHE_NAME = 'blackrose-v3'
const GUIDE_CACHE = 'blackrose-guides-v3'

const API_CACHE_PATTERNS = [
  /\/api\/guide\/[^/]+$/,
  /\/api\/categories$/,
  /\/api\/category\/[^/]+$/,
]

self.addEventListener('install', e => {
  self.skipWaiting()
})

self.addEventListener('activate', e => {
  // Удаляем ВСЕ старые кеши включая v1 и v2
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', e => {
  const { request } = e
  const url = new URL(request.url)

  if (request.method !== 'GET') return

  // Только API гайды кешируем (network-first)
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

  // Вся статика (JS, CSS, HTML) — всегда с сервера, без кеша
  // Это гарантирует что новый bundle всегда загружается после деплоя
})
