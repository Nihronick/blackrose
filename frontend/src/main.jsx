import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { initTheme } from './theme'
import { App } from './App'
import './index.css'

initTheme()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// Service Worker registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}
