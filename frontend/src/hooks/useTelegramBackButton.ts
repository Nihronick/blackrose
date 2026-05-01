import { haptic } from '@/lib/haptic'
import { tgApp } from '@/lib/theme'
import { useCallback, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export const useTelegramBackButton = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleBack = useCallback(() => {
    haptic.light()
    if (location.pathname === '/') {
      tgApp?.close?.()
    } else {
      navigate(-1)
    }
  }, [location.pathname, navigate])

  useEffect(() => {
    const noBack = location.pathname === '/'
    const backBtn = tgApp?.BackButton

    if (noBack) {
      backBtn?.hide()
    } else {
      backBtn?.show()
    }

    backBtn?.offClick(handleBack)
    backBtn?.onClick(handleBack)

    return () => backBtn?.offClick(handleBack)
  }, [location.pathname, handleBack])

  return { handleBack }
}
