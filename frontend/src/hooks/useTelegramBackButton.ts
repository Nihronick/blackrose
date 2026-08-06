import { useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

/**
 * Simple back button handler for web navigation.
 * Uses standard browser history with BrowserRouter (clean URLs).
 */
export const useTelegramBackButton = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleBack = useCallback(() => {
    const currentPath = location.pathname
    if (currentPath === '/') return

    // Check if there is history to go back to
    if (window.history.length > 1) {
      window.history.back()
    }

    // Fallback logic if history didn't change (e.g. direct URL entry)
    setTimeout(() => {
      if (window.location.pathname === currentPath) {
        if (currentPath.startsWith('/guilds/')) {
          navigate('/guilds', { replace: true })
        } else if (currentPath.startsWith('/category/')) {
          navigate('/', { replace: true })
        } else if (currentPath.startsWith('/guide/')) {
          navigate('/', { replace: true })
        } else {
          navigate('/', { replace: true })
        }
      }
    }, 120)
  }, [location.pathname, navigate])

  return { handleBack }
}
