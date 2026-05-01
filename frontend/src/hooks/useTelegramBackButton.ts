import { haptic } from '@/lib/haptic'
import { tgApp } from '@/lib/theme'
import { useCallback, useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export const useTelegramBackButton = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const lastPathname = useRef(location.pathname)

  const handleBack = useCallback(() => {
    haptic.light()
    
    // Если мы на главной, кнопка назад (если она вдруг видна) закрывает приложение
    if (location.pathname === '/') {
      tgApp?.close?.()
      return
    }

    // Проверяем, есть ли куда возвращаться в истории именно нашего приложения
    // В React Router v6 navigate(-1) может не сработать, если нет истории
    // Мы пробуем вернуться назад, но если мы зашли по прямой ссылке, идем на главную
    if (window.history.state && window.history.state.idx > 0) {
      navigate(-1)
    } else {
      navigate('/', { replace: true })
    }
  }, [location.pathname, navigate])

  useEffect(() => {
    const isHome = location.pathname === '/'
    const backBtn = tgApp?.BackButton

    if (!backBtn) return

    if (isHome) {
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
