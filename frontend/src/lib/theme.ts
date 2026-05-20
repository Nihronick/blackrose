/** Desktop theme: detect system dark/light mode and sync viewport height. */

function syncAppViewportHeight() {
  const h = window.visualViewport?.height ?? window.innerHeight
  if (h && h > 0) {
    document.documentElement.style.setProperty('--app-vh', `${h}px`)
  }
}

export function initTheme() {
  // Detect system dark mode
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light')
  })

  // Keep --app-vh in sync for mobile browsers
  syncAppViewportHeight()
  window.addEventListener('resize', syncAppViewportHeight)
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', syncAppViewportHeight)
  }
}
