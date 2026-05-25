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
    if (location.pathname === '/') {
      return
    }

    const currentPath = window.location.pathname
    window.history.back()

    // If pathname didn't change after back(), there's no history — go home
    setTimeout(() => {
      if (window.location.pathname === currentPath) {
        navigate('/', { replace: true })
      }
    }, 150)
  }, [location.pathname, navigate])

  return { handleBack }
}
