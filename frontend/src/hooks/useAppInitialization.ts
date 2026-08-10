import { apiFetch } from '@/lib/api'
import { clearStoredToken, getMode, getStoredUser } from '@/lib/auth'
import { applyLanguageKey } from '@/lib/language'
import { initTelegramApp } from '@/lib/telegram'
import { useAppStore } from '@/store'
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export const useAppInitialization = () => {
  const navigate = useNavigate()
  const { language, setIsAdmin } = useAppStore()

  useEffect(() => {
    let isCancelled = false

    // Initialize modern Telegram Mini App 8.x features (Fullscreen, Deep Linking, Color Sync)
    initTelegramApp(navigate)

    const doAuth = async () => {
      if (isCancelled) return

      const mode = getMode()

      // Web mode: apply stored user immediately
      if (mode === 'web') {
        pipe(
          getStoredUser(),
          O.map((user) => {
            if (user.is_admin) setIsAdmin(true)
          })
        )
      }

      // Silent backend check for token validity
      apiFetch<{ is_admin?: boolean }>('/api/auth/web-check')
        .then((data) => {
          if (isCancelled) return
          if (data?.is_admin === true) setIsAdmin(true)
        })
        .catch((e) => {
          if (e.message?.includes('Сессия истекла') || e.message === 'ACCESS_DENIED') {
            clearStoredToken()
          }
        })
    }

    const openDeepLink = async () => {
      const params = new URLSearchParams(window.location.search)
      const deepGuide = params.get('guide')
      if (!deepGuide) return

      const guideKey = deepGuide.startsWith('ru_')
        ? deepGuide
        : applyLanguageKey(deepGuide, language)

      const payload = await apiFetch<{ categories?: { key: string }[] }>('/api/categories').catch(
        () => null
      )
      const categories = Array.isArray(payload?.categories) ? payload.categories : []
      const category = categories.find((c: { key: string }) => c.key === guideKey)

      if (category) {
        navigate(`/category/${encodeURIComponent(guideKey)}`)
        return
      }

      navigate(`/guide/${encodeURIComponent(guideKey)}`)
    }

    // Run auth immediately — no SDK to wait for
    doAuth()
    openDeepLink()

    return () => {
      isCancelled = true
    }
  }, [language, navigate, setIsAdmin])

  useEffect(() => {
    navigator.serviceWorker?.register?.('sw.js').catch(() => {})
  }, [])
}
