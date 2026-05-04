import { useAppEnv } from '@/hooks/useAppEnv'
import { apiFetch } from '@/lib/api'
import {
  clearStoredToken,
  getMode,
  getStoredUser,
  getTelegramInitData,
  hasTelegramWebApp,
  isTelegram,
  setStoredToken,
} from '@/lib/auth'
import { applyLanguageKey } from '@/lib/language'
import { useAppStore } from '@/store'
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export const useAppInitialization = () => {
  const navigate = useNavigate()
  const { language, setIsAdmin } = useAppStore()
  const inTelegram = hasTelegramWebApp()

  useEffect(() => {
    let isCancelled = false
    let retryTimer: number | null = null
    let attempts = 0
    const maxAttempts = 8

    const scheduleRetry = () => {
      if (isCancelled || attempts >= maxAttempts) return
      attempts += 1
      retryTimer = window.setTimeout(doAuth, 450)
    }

    const doAuth = async () => {
      if (isCancelled) return

      const mode = getMode()
      const initData = getTelegramInitData()

      // 1. Если в TMA — обмениваем данные на JWT (Exchange Strategy)
      if (initData) {
        try {
          interface TmaLoginResponse {
            token: string
            user_id: number
            first_name: string
            is_admin: boolean
          }
          const data = await apiFetch<TmaLoginResponse>('/api/auth/tma-login', { method: 'POST' })
          if (data?.token && !isCancelled) {
            setStoredToken(data.token, {
              id: data.user_id,
              first_name: data.first_name,
              is_admin: data.is_admin,
            })
            if (data.is_admin) setIsAdmin(true)
          }
        } catch (e) {
          console.warn('TMA JWT Exchange failed, falling back to initData only:', e)
        }
      }
      // 2. Веб-режим: сразу применяем сохранённый токен
      else if (mode === 'web') {
        pipe(
          getStoredUser(),
          O.map((user) => {
            if (user.is_admin) setIsAdmin(true)
          })
        )
      }

      // Тихая проверка актуальности на бэкенде
      apiFetch<{ is_admin?: boolean }>('/api/auth/web-check')
        .then((data) => {
          if (isCancelled) return
          if (data?.is_admin === true) setIsAdmin(true)
        })
        .catch((e) => {
          if (e.message?.includes('Сессия истекла')) clearStoredToken()

          // Telegram SDK может инициализироваться с задержкой: даём несколько попыток.
          if (inTelegram && !getTelegramInitData()) scheduleRetry()
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

    const tgWindow = window as unknown as Window & {
      __tgSdkLoaded?: boolean
      __tgSdkFailed?: boolean
    }
    tgWindow.addEventListener('tgSdkReady', doAuth)
    if (tgWindow.__tgSdkLoaded || tgWindow.__tgSdkFailed) doAuth()
    else if (!inTelegram) setTimeout(doAuth, 100)
    else scheduleRetry()

    openDeepLink()

    return () => {
      isCancelled = true
      if (retryTimer) window.clearTimeout(retryTimer)
      tgWindow.removeEventListener('tgSdkReady', doAuth)
    }
  }, [language, navigate, setIsAdmin, inTelegram])

  useEffect(() => {
    navigator.serviceWorker?.register?.('sw.js').catch(() => {})
  }, [])
}
