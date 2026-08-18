import { useCallback, useEffect, useState } from 'react'
import { apiFetch } from '../lib/api'
import { storage } from '../lib/storage'
import { useAppStore } from '../store'

const STORAGE_KEY = 'blackrose_favorites'

export interface FavoriteGuide {
  key: string
  title: string
  icon?: string
}

export function useFavorites() {
  const [favorites, setFavorites] = useState<FavoriteGuide[]>([])
  const [loaded, setLoaded] = useState(false)
  const user = useAppStore((s) => s.user)

  // 1. Load local favorites first
  useEffect(() => {
    storage.get(STORAGE_KEY).then((val) => {
      if (val) {
        try {
          setFavorites(JSON.parse(val))
        } catch {
          setFavorites([])
        }
      }
      setLoaded(true)
    })
  }, [])

  // 2. Sync with cloud if user is authenticated
  useEffect(() => {
    if (!user) return
    apiFetch<{ favorites: Array<{ key: string; title: string; icon_url?: string }> }>('/user/favorites')
      .then((res) => {
        if (res.favorites && Array.isArray(res.favorites)) {
          setFavorites((prev) => {
            const map = new Map<string, FavoriteGuide>()
            for (const f of prev) map.set(f.key, f)
            for (const f of res.favorites) {
              map.set(f.key, { key: f.key, title: f.title, icon: f.icon_url })
            }
            const merged = Array.from(map.values())
            storage.set(STORAGE_KEY, JSON.stringify(merged))
            return merged
          })
        }
      })
      .catch(() => {
        // offline or non-blocking
      })
  }, [user])

  const toggle = useCallback(
    async (guide: FavoriteGuide) => {
      const exists = favorites.some((f) => f.key === guide.key)
      const next = exists
        ? favorites.filter((f) => f.key !== guide.key)
        : [...favorites, { key: guide.key, title: guide.title, icon: guide.icon }]

      setFavorites(next)
      storage.set(STORAGE_KEY, JSON.stringify(next))

      // Sync with cloud in background if user is authenticated
      if (user) {
        if (exists) {
          apiFetch(`/user/favorites/${guide.key}`, { method: 'DELETE' }).catch(() => {})
        } else {
          apiFetch(`/user/favorites/${guide.key}`, { method: 'POST' }).catch(() => {})
        }
      }
    },
    [favorites, user]
  )

  const isFavorite = useCallback(
    (key: string) => {
      return favorites.some((f) => f.key === key)
    },
    [favorites]
  )

  return { favorites, loaded, toggle, isFavorite }
}
