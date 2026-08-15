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

    // 0. Intercept Telegram Inline Login URL parameters (?id=...&hash=...&auth_date=...)
    try {
      const urlParams = new URLSearchParams(window.location.search)
      const tgId = urlParams.get('id')
      const tgHash = urlParams.get('hash')
      const tgAuthDate = urlParams.get('auth_date')

      if (tgId && tgHash && tgAuthDate) {
        const payload = {
          id: Number(tgId),
          first_name: urlParams.get('first_name') || '',
          last_name: urlParams.get('last_name') || undefined,
          username: urlParams.get('username') || undefined,
          photo_url: urlParams.get('photo_url') || undefined,
          auth_date: Number(tgAuthDate),
          hash: tgHash,
        }

        apiFetch<{
          ok?: boolean
          token?: string
          refresh_token?: string
          user_id?: number
          first_name?: string
          username?: string
          photo_url?: string
          is_admin?: boolean
        }>('/api/auth/web-login', {
          method: 'POST',
          body: JSON.stringify(payload),
        })
          .then((data) => {
            if (data?.token && data.user_id) {
              setStoredToken(
                data.token,
                {
                  id: data.user_id,
                  first_name: data.first_name || 'Слеер',
                  username: data.username,
                  photo_url: data.photo_url,
                  is_admin: !!data.is_admin,
                },
                data.refresh_token
              )
              if (data.is_admin) setIsAdmin(true)

              // Clean URL parameters from address bar
              const cleanUrl = new URL(window.location.href)
              cleanUrl.searchParams.delete('id')
              cleanUrl.searchParams.delete('first_name')
              cleanUrl.searchParams.delete('last_name')
              cleanUrl.searchParams.delete('username')
              cleanUrl.searchParams.delete('photo_url')
              cleanUrl.searchParams.delete('auth_date')
              cleanUrl.searchParams.delete('hash')
              window.history.replaceState({}, '', cleanUrl.toString())
            }
          })
          .catch((err) => {
            console.warn('Telegram Inline Login error:', err)
          })
      }
    } catch {}

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
