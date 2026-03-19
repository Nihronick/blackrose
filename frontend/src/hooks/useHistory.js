import { useState, useEffect, useCallback } from 'react'

const MAX_HISTORY = 20
const STORAGE_KEY = 'blackrose_history'
const tg = window.Telegram?.WebApp

function csGet(key) {
  return new Promise(resolve => {
    if (!tg?.CloudStorage) { resolve(null); return }
    tg.CloudStorage.getItem(key, (err, val) => resolve(err ? null : val))
  })
}
function csSet(key, value) {
  return new Promise(resolve => {
    if (!tg?.CloudStorage) { resolve(false); return }
    tg.CloudStorage.setItem(key, value, err => resolve(!err))
  })
}

export function useHistory() {
  const [history, setHistory] = useState([])

  useEffect(() => {
    csGet(STORAGE_KEY).then(val => {
      if (val) {
        try { setHistory(JSON.parse(val)) } catch { setHistory([]) }
      }
    })
  }, [])

  const addToHistory = useCallback((guide) => {
    if (!guide?.key) return
    setHistory(prev => {
      // Remove existing entry for same key, then prepend
      const filtered = prev.filter(g => g.key !== guide.key)
      const next = [{ key: guide.key, title: guide.title, icon: guide.icon }, ...filtered]
        .slice(0, MAX_HISTORY)
      csSet(STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }, [])

  const clearHistory = useCallback(() => {
    setHistory([])
    csSet(STORAGE_KEY, '[]')
  }, [])

  return { history, addToHistory, clearHistory }
}
