import { useCallback, useEffect, useState } from 'react'
import { storage } from '../lib/storage'

const MAX_SEARCH_HISTORY = 10
const STORAGE_KEY = 'blackrose_search_history'

export function useSearchHistory() {
  const [searchHistory, setSearchHistory] = useState<string[]>([])
  const [isInitialized, setIsInitialized] = useState(false)

  // 1. Initial Load
  useEffect(() => {
    let active = true
    storage.get(STORAGE_KEY).then((val) => {
      if (!active) return
      if (val) {
        try {
          const parsed = JSON.parse(val)
          if (Array.isArray(parsed)) {
            setSearchHistory(parsed)
          }
        } catch (e) {
          console.error('[SearchHistory] Failed to parse history:', e)
          setSearchHistory([])
        }
      }
      setIsInitialized(true)
    })
    return () => { active = false }
  }, [])

  // 2. Sync to Storage (Side Effect)
  // We only sync after initialization to avoid overwriting cloud data with initial empty state
  useEffect(() => {
    if (isInitialized) {
      storage.set(STORAGE_KEY, JSON.stringify(searchHistory)).catch(e => {
        console.error('[SearchHistory] Sync failed:', e)
      })
    }
  }, [searchHistory, isInitialized])

  const addToSearchHistory = useCallback((query: string) => {
    const q = query.trim()
    if (!q || q.length < 2) return
    
    setSearchHistory((prev) => {
      const filtered = prev.filter((item) => item.toLowerCase() !== q.toLowerCase())
      return [q, ...filtered].slice(0, MAX_SEARCH_HISTORY)
    })
  }, [])

  const removeFromSearchHistory = useCallback((query: string) => {
    setSearchHistory((prev) => prev.filter((item) => item !== query))
  }, [])

  const clearSearchHistory = useCallback(() => {
    setSearchHistory([])
  }, [])

  return { 
    searchHistory, 
    isInitialized,
    addToSearchHistory, 
    removeFromSearchHistory, 
    clearSearchHistory 
  }
}
