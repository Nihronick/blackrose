import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { App } from './App'
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
    reportData: import.meta.env.PROD,
    ignoreErrors: [
      'ERR_INSUFFICIENT_RESOURCES',
      'Failed to fetch dynamically imported module',
      'ResizeObserver loop limit exceeded',
      'NetworkError when attempting to fetch resource',
    ],
  })
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes garbage collection for unused cache
      retry: (failureCount, error: unknown) => {
        if (error instanceof Error && error.message === 'ACCESS_DENIED') return false
        if (error instanceof Error && error.message?.includes('Сессия истекла')) return false
        return failureCount < 1
      },
      refetchOnWindowFocus: false,
    },
  },
})

import { isNative, setStatusBarDark, initDeepLinks } from './lib/capacitor'

initTheme()

if (isNative()) {
  setStatusBarDark()
  initDeepLinks((path: string) => {
    window.history.pushState(null, '', path)
    window.dispatchEvent(new PopStateEvent('popstate'))
  })
}

const rootElement = document.getElementById('root')
if (rootElement) {
  createRoot(rootElement).render(
    <StrictMode>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <AppEnvProvider>
              <App />
            </AppEnvProvider>
          </BrowserRouter>
        </QueryClientProvider>
      </ErrorBoundary>
    </StrictMode>
  )
}
