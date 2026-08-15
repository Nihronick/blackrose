import type { TelegramWebApp } from '../globals'

/**
 * Safely returns the Telegram WebApp instance if available
 */
export function getTelegramWebApp(): TelegramWebApp | null {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp
  }
  return null
}

/**
 * Triggers Haptic Feedback for TMA
 */
export function hapticImpact(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'light') {
  const tg = getTelegramWebApp()
  if (tg?.HapticFeedback) {
    try {
      tg.HapticFeedback.impactOccurred(style)
    } catch {
      // Ignore fallback
    }
  }
}

export function hapticNotification(type: 'success' | 'warning' | 'error') {
  const tg = getTelegramWebApp()
  if (tg?.HapticFeedback) {
    try {
      tg.HapticFeedback.notificationOccurred(type)
    } catch {
      // Ignore fallback
    }
  }
}

/**
 * Initializes all modern Telegram Mini App 8.x features:
 * 1. Fullscreen / Expansion
 * 2. Theme color sync
 * 3. Native BackButton listener
 * 4. Deep linking via start_param
 */
export function initTelegramApp(navigate?: (path: string) => void) {
  const tg = getTelegramWebApp()
  if (!tg) return

  try {
    // 1. Notify Telegram WebApp is ready
    tg.ready()

    // 2. Expand / Request Fullscreen for maximum native feel
    if (tg.isVersionAtLeast && tg.isVersionAtLeast('8.0') && tg.requestFullscreen) {
      try {
        tg.requestFullscreen()
      } catch {
        // Fallback
      }
    } else if (tg.expand) {
      try {
        tg.expand()
      } catch {
        // Fallback
      }
    }

    // 3. Enable closing confirmation when navigating
    if (tg.isVersionAtLeast && tg.isVersionAtLeast('6.2') && tg.enableClosingConfirmation) {
      try {
        tg.enableClosingConfirmation()
      } catch {
        // Fallback
      }
    }

    // 4. Color sync
    const isDark = document.documentElement.classList.contains('dark')
    const headerColor = isDark ? '#141419' : '#ffffff'
    const bgColor = isDark ? '#101014' : '#fafafa'

    if (tg.setHeaderColor) tg.setHeaderColor(headerColor)
    if (tg.setBackgroundColor) tg.setBackgroundColor(bgColor)

    // 5. Deep linking via start_param
    const startParam = tg.initDataUnsafe?.start_param
    if (startParam && navigate) {
      if (startParam.startsWith('guild_')) {
        const guildId = startParam.replace('guild_', '')
        navigate(`/guilds/${guildId}`)
      } else if (startParam.startsWith('guide_')) {
        const guideKey = startParam.replace('guide_', '')
        navigate(`/guide/${guideKey}`)
      } else if (startParam === 'guilds') {
        navigate('/guilds')
      }
    }
  } catch (e) {
    console.warn('Telegram WebApp init warning:', e)
  }
}

/**
 * Syncs native Telegram BackButton with React Router
 */
export function useTelegramBackButton(show: boolean, onBack: () => void) {
  const tg = getTelegramWebApp()
  if (!tg || !tg.BackButton) return

  try {
    if (show) {
      tg.BackButton.show()
      tg.BackButton.onClick(onBack)
    } else {
      tg.BackButton.hide()
      tg.BackButton.offClick(onBack)
    }
  } catch {
    // Ignore fallback
  }
}
