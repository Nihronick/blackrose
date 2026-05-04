import { useAppEnv } from '@/hooks/useAppEnv'
import { tgApp } from '@/lib/theme'
import { useCallback, useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export const useTelegramBackButton = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const lastPathname = useRef(location.pathname)

  const { isTMA, tg } = useAppEnv()

  const handleBack = useCallback(() => {
    try {
      if (tg?.HapticFeedback) {
        tg.HapticFeedback.impactOccurred('light')
      }
    } catch (e) {}

    if (location.pathname === '/') {
      tg?.close?.()
      return
    }

    // Если в истории только одна запись, history.back() ничего не сделает.
    // Поэтому запоминаем текущий путь и проверяем через таймаут.
    const currentPath = window.location.hash
    window.history.back()

    setTimeout(() => {
      // Если хеш не изменился - значит истории не было, идем на главную принудительно
      if (window.location.hash === currentPath) {
        navigate('/', { replace: true })
      }
    }, 150)
  }, [location.pathname, navigate, tg])

  useEffect(() => {
    const isHome = location.pathname === '/'
    const backBtn = tg?.BackButton

    if (!backBtn) return

    if (isHome || !isTMA) {
      backBtn.hide()
    } else {
      backBtn.show()
    }

    // Важно: удаляем старый обработчик перед добавлением нового,
    // чтобы не было стака вызовов при изменении pathname
    backBtn.offClick(handleBack)
    backBtn.onClick(handleBack)

    return () => {
      backBtn.offClick(handleBack)
    }
  }, [location.pathname, handleBack])

  return { handleBack }
}
