import { useCallback, useEffect, useState } from 'react'
import { storage } from '../lib/storage'

const STORAGE_KEY = 'blackrose_favorites'

export interface FavoriteGuide {
  key: string
  title: string
  icon?: string
}

export function useFavorites() {
  const [favorites, setFavorites] = useState<FavoriteGuide[]>([])
  const [loaded, setLoaded] = useState(false)

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

  const toggle = useCallback(async (guide: FavoriteGuide) => {
    setFavorites((prev) => {
      const exists = prev.some((f) => f.key === guide.key)
      const next = exists
        ? prev.filter((f) => f.key !== guide.key)
        : [...prev, { key: guide.key, title: guide.title, icon: guide.icon }]

      storage.set(STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }, [])

  const isFavorite = useCallback(
    (key: string) => {
      return favorites.some((f) => f.key === key)
    },
    [favorites]
  )

  return { favorites, loaded, toggle, isFavorite }
}
