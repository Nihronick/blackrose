import { useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'blackrose_favorites'
const tg = window.Telegram?.WebApp

// ── Storage helpers: CloudStorage (Telegram) → localStorage (desktop) ──

function csGet(key) {
  return new Promise((resolve) => {
    if (tg?.CloudStorage) {
      tg.CloudStorage.getItem(key, (err, val) => resolve(err ? null : val))
    } else {
      resolve(localStorage.getItem(key))
    }
  })
}

function csSet(key, value) {
  return new Promise((resolve) => {
    if (tg?.CloudStorage) {
      tg.CloudStorage.setItem(key, value, (err) => resolve(!err))
    } else {
      try { localStorage.setItem(key, value); resolve(true) }
      catch { resolve(false) }
    }
  })
}

export function useFavorites() {
  const [favorites, setFavorites] = useState([])
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    csGet(STORAGE_KEY).then(val => {
      if (val) {
        try { setFavorites(JSON.parse(val)) } catch { setFavorites([]) }
      }
      setLoaded(true)
    })
  }, [])

  const toggle = useCallback(async (guide) => {
    setFavorites(prev => {
      const exists = prev.some(f => f.key === guide.key)
      const next = exists
        ? prev.filter(f => f.key !== guide.key)
        : [...prev, { key: guide.key, title: guide.title, icon: guide.icon }]
      csSet(STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }, [])

  const isFavorite = useCallback((key) => {
    return favorites.some(f => f.key === key)
  }, [favorites])

  return { favorites, loaded, toggle, isFavorite }
}
