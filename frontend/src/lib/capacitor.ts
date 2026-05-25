/**
 * capacitor.js — нативные функции для мобильного приложения.
 * Автоматически определяет платформу и использует нативные API
 * или заглушки для веба/Telegram.
 */

import Honeybadger from '@honeybadger-io/js'

// Определяем платформу
export const isNative = () => {
  try {
    return window.Capacitor?.isNativePlatform?.() ?? false
  } catch {
    return false
  }
}

export const isAndroid = () => {
  try {
    return window.Capacitor?.getPlatform?.() === 'android'
  } catch {
    return false
  }
}

export const isIos = () => {
  try {
    return window.Capacitor?.getPlatform?.() === 'ios'
  } catch {
    return false
  }
}

// ── Haptic feedback ─────────────────────────────────────────
// Нативный на мобиле, Telegram WebApp API в Mini App, заглушка в вебе

export const hapticLight = async () => {
  if (isNative()) {
    const { Haptics, ImpactStyle } = await import('@capacitor/haptics')
    await Haptics.impact({ style: ImpactStyle.Light })
  }
}

export const hapticMedium = async () => {
  if (isNative()) {
    const { Haptics, ImpactStyle } = await import('@capacitor/haptics')
    await Haptics.impact({ style: ImpactStyle.Medium })
  }
}

// ── Push notifications ────────────────────────────────────
export const initPushNotifications = async (onToken: (t: string) => void) => {
  if (!isNative()) return

  try {
    const { PushNotifications } = await import('@capacitor/push-notifications')

    const permission = await PushNotifications.requestPermissions()
    if (permission.receive !== 'granted') return

    await PushNotifications.register()

    PushNotifications.addListener('registration', (token) => {
      onToken?.(token.value)
    })

    PushNotifications.addListener('pushNotificationReceived', (notification) => {
      // Notification received - handled by push service
    })

    PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
      const url = action.notification.data?.url
      if (url) {
        window.history.pushState(null, '', url)
        window.dispatchEvent(new PopStateEvent('popstate'))
      }
    })
  } catch (e) {
    if (import.meta.env.VITE_HONEYBADGER_API_KEY) {
      Honeybadger.notify(new Error('Push notifications initialization failed'), {
        context: { originalError: e },
      })
    }
  }
}

// ── Status bar ──────────────────────────────────────────
export const setStatusBarDark = async () => {
  if (!isNative()) return
  try {
    const { StatusBar, Style } = await import('@capacitor/status-bar')
    await StatusBar.setStyle({ style: Style.Dark })
    await StatusBar.setBackgroundColor({ color: '#1c1c1e' })
  } catch {}
}

// ── App URL open (deep links) ───────────────────────────
export const initDeepLinks = (onUrl: (u: string) => void) => {
  if (!isNative()) return
  import('@capacitor/app')
    .then(({ App }) => {
      App.addListener('appUrlOpen', (event) => {
        // blackrose://guide/slug → /guide/slug
        const url = new URL(event.url)
        const path = url.pathname
        onUrl?.(path)
      })
    })
    .catch(() => {})
}
