import { useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

/**
 * Smart back button handler for SPA web & TMA navigation.
 * Respects React Router session stack and provides hierarchical fallback when history is unavailable.
 */
export const useTelegramBackButton = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleBack = useCallback(() => {
    const currentPath = location.pathname
    if (currentPath === '/') return

    // If navigated within this SPA session (key is not default), go back in router history
    if (location.key !== 'default') {
      navigate(-1)
      return
    }

    // Direct entry or refresh fallback: navigate hierarchically
    if (currentPath.startsWith('/guilds/')) {
      navigate('/guilds', { replace: true })
    } else if (currentPath.startsWith('/guide/')) {
      navigate('/categories', { replace: true })
    } else if (currentPath.startsWith('/category/')) {
      navigate('/categories', { replace: true })
    } else if (currentPath.startsWith('/tag/')) {
      navigate('/search', { replace: true })
    } else {
      navigate('/', { replace: true })
    }
  }, [location.key, location.pathname, navigate])

  return { handleBack }
}
