import { useCallback, useEffect, useState } from 'react'
import { storage } from '../lib/storage'

const MAX_HISTORY = 20
const STORAGE_KEY = 'blackrose_history'

export interface HistoryItem {
  key: string
  title: string
  icon?: string
}

export function useHistory() {
  const [history, setHistory] = useState<HistoryItem[]>([])

  useEffect(() => {
    storage.get(STORAGE_KEY).then((val) => {
      if (val) {
        try {
          setHistory(JSON.parse(val))
        } catch {
          setHistory([])
        }
      }
    })
  }, [])

  const addToHistory = useCallback((guide: HistoryItem) => {
    if (!guide?.key) return
    setHistory((prev) => {
      const filtered = prev.filter((g) => g.key !== guide.key)
      const next = [{ key: guide.key, title: guide.title, icon: guide.icon }, ...filtered].slice(
        0,
        MAX_HISTORY
      )
      storage.set(STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }, [])

  const clearHistory = useCallback(() => {
    setHistory([])
    storage.set(STORAGE_KEY, '[]')
  }, [])

  return { history, addToHistory, clearHistory }
}
