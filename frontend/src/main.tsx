import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
import { ErrorBoundary } from './components/ErrorBoundary'
import { AppEnvProvider } from './hooks/useAppEnv'
import { initTheme } from './lib/theme'
import './index.css'
// import '@fontsource-variable/geist'

import Honeybadger from '@honeybadger-io/js'

const HB_API_KEY = import.meta.env.VITE_HONEYBADGER_API_KEY
if (HB_API_KEY) {
  Honeybadger.configure({
    apiKey: HB_API_KEY,
    environment: import.meta.env.PROD ? 'production' : 'development',
    reportData: !!window.Telegram?.WebApp?.initData,
  })
  window.addEventListener('error', (e) => {
    if (e.error) Honeybadger.notify(e.error)
  })
  window.addEventListener('unhandledrejection', (e) => {
    Honeybadger.notify(e.reason instanceof Error ? e.reason : new Error(String(e.reason)))
  })
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: unknown) => {
        if (error instanceof Error && error.message === 'ACCESS_DENIED') return false
        if (error instanceof Error && error.message?.includes('Сессия истекла')) return false
        return failureCount < 1
      },
      refetchOnWindowFocus: false,
    },
  },
})

initTheme()

// @ts-ignore
import('./lib/capacitor')
  .then(({ isNative, setStatusBarDark, initDeepLinks }) => {
    if (isNative()) {
      setStatusBarDark()
      initDeepLinks((path: string) => {
        window.location.hash = path
      })
    }
  })
  .catch(() => {})

const rootElement = document.getElementById('root')
if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <HashRouter>
            <AppEnvProvider>
              <App />
            </AppEnvProvider>
          </HashRouter>
        </QueryClientProvider>
      </ErrorBoundary>
    </StrictMode>
  )
}
