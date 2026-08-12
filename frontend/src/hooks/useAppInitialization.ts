import { apiFetch } from '@/lib/api'
import { clearStoredToken, getMode, getStoredUser, setStoredToken } from '@/lib/auth'
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

    const tgUser =
      typeof window !== 'undefined'
        ? (
            window as unknown as {
              Telegram?: {
                WebApp?: {
                  initDataUnsafe?: {
                    user?: { first_name?: string; username?: string; id?: number }
                  }
                }
              }
            }
          ).Telegram?.WebApp?.initDataUnsafe?.user
        : undefined
    if (tgUser) {
      const name = tgUser.username || tgUser.first_name
      if (name && !localStorage.getItem('slayer_nickname')) {
        localStorage.setItem('slayer_nickname', name)
      }
    }

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

      // Backend check for Telegram / Token admin status
      apiFetch<{
        authorized?: boolean
        user_id?: number
        first_name?: string
        username?: string
        is_admin?: boolean
        token?: string
      }>('/api/auth')
        .then((data) => {
          if (isCancelled) return
          if (data?.authorized && data.user_id) {
            const userObj = {
              id: data.user_id,
              first_name: data.first_name || tgUser?.first_name || 'Слеер',
              username: data.username || tgUser?.username,
              is_admin: !!data.is_admin,
            }
            if (data.token) {
              setStoredToken(data.token, userObj)
            } else {
              localStorage.setItem('br_user', JSON.stringify(userObj))
            }
            if (data.is_admin) {
              setIsAdmin(true)
            }
          }
        })
        .catch(() => {})
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
