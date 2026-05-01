import Honeybadger from '@honeybadger-io/js'

export const tgApp = window.Telegram?.WebApp

/** Высота области WebApp (устраняет обрезание на мобильных при 100vh). */
function syncAppViewportHeight() {
  const tg = window.Telegram?.WebApp
  const h =
    tg?.viewportStableHeight ??
    tg?.viewportHeight ??
    window.visualViewport?.height ??
    window.innerHeight
  if (h && h > 0) {
    document.documentElement.style.setProperty('--app-vh', `${h}px`)
  }
}

/** Отступы под вырезы / home indicator (Telegram 6.1+ или env() в браузере). */
function syncSafeAreaInsets() {
  const tg = window.Telegram?.WebApp
  const r = document.documentElement.style
  const inset = tg?.contentSafeAreaInset ?? tg?.safeAreaInset
  if (inset && typeof inset === 'object') {
    r.setProperty('--safe-top', `${Number(inset.top) || 0}px`)
    r.setProperty('--safe-bottom', `${Number(inset.bottom) || 0}px`)
    r.setProperty('--safe-left', `${Number(inset.left) || 0}px`)
    r.setProperty('--safe-right', `${Number(inset.right) || 0}px`)
  }
}

export function initTheme() {
  const tg = tgApp

  // ── Desktop fallback: detect system dark mode ─────────────
  if (!tg?.initData) {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light')
    })
    syncAppViewportHeight()
    window.addEventListener('resize', syncAppViewportHeight)
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', syncAppViewportHeight)
    }
    return
  }

  // ── Telegram WebApp theme ─────────────────────────────────
  try {
    tg.ready()
    tg.expand()
    document.documentElement.setAttribute('data-theme', tg.colorScheme || 'light')
    const p = tg.themeParams || {}
    const r = document.documentElement.style
    if (p.bg_color) r.setProperty('--bg', p.bg_color)
    if (p.text_color) r.setProperty('--text', p.text_color)
    if (p.hint_color) r.setProperty('--text-secondary', p.hint_color)
    if (p.button_color) r.setProperty('--accent', p.button_color)
    if (p.button_text_color) r.setProperty('--accent-text', p.button_text_color)
    if (p.secondary_bg_color) {
      r.setProperty('--surface', p.secondary_bg_color)
      r.setProperty('--surface2', p.secondary_bg_color)
    }

    syncAppViewportHeight()
    syncSafeAreaInsets()
    tg.onEvent?.('viewportChanged', syncAppViewportHeight)
    tg.onEvent?.('safeAreaChanged', syncSafeAreaInsets)
  } catch (e) {
    if (import.meta.env.VITE_HONEYBADGER_API_KEY) {
      Honeybadger.notify(new Error('Theme initialization failed'), {
        context: { originalError: e },
      })
    }
  }
}
