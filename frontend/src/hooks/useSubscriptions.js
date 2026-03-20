import { useState, useEffect, useCallback } from 'react'
import { apiGetSubscriptions, apiSubscribe, apiUnsubscribe } from '../api'

export function useSubscriptions() {
  const [subs, setSubs]     = useState([])
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    apiGetSubscriptions()
      .then(res => setSubs(res.subscriptions || []))
      .catch(() => {})
      .finally(() => setLoaded(true))
  }, [])

  const isSubscribed = useCallback((key) => subs.includes(key), [subs])

  const toggle = useCallback(async (categoryKey) => {
    const was = subs.includes(categoryKey)
    // Optimistic update
    setSubs(s => was ? s.filter(k => k !== categoryKey) : [...s, categoryKey])
    try {
      if (was) await apiUnsubscribe(categoryKey)
      else await apiSubscribe(categoryKey)
    } catch {
      // Rollback
      setSubs(s => was ? [...s, categoryKey] : s.filter(k => k !== categoryKey))
    }
  }, [subs])

  return { subs, loaded, isSubscribed, toggle }
}
