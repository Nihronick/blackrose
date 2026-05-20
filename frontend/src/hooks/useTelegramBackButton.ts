import { useCallback } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

/**
 * Simple back button handler for web navigation.
 * Previously integrated with Telegram BackButton API — now uses standard browser history.
 */
export const useTelegramBackButton = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleBack = useCallback(() => {
    if (location.pathname === '/') {
      return
    }

    const currentPath = window.location.hash
    window.history.back()

    // If hash didn't change after back(), there's no history — go home
    setTimeout(() => {
      if (window.location.hash === currentPath) {
        navigate('/', { replace: true })
      }
    }, 150)
  }, [location.pathname, navigate])

  return { handleBack }
}
