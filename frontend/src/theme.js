export const tgApp = window.Telegram?.WebApp

export function initTheme() {
  const tg = tgApp
  if (!tg) return
  try {
    tg.ready()
    tg.expand()
    document.documentElement.setAttribute('data-theme', tg.colorScheme || 'light')
    const p = tg.themeParams || {}
    const r = document.documentElement.style
    if (p.bg_color)           r.setProperty('--bg', p.bg_color)
    if (p.text_color)         r.setProperty('--text', p.text_color)
    if (p.hint_color)         r.setProperty('--text-secondary', p.hint_color)
    if (p.button_color)       r.setProperty('--accent', p.button_color)
    if (p.button_text_color)  r.setProperty('--accent-text', p.button_text_color)
    if (p.secondary_bg_color) {
      r.setProperty('--surface', p.secondary_bg_color)
      r.setProperty('--surface2', p.secondary_bg_color)
    }
  } catch (e) {
    console.warn('Theme init:', e)
  }
}
