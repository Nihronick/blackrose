import { useAppInitialization } from '@/hooks/useAppInitialization'
import { useAppStore } from '@/store'
import { type FC, type ReactNode, useEffect } from 'react'
import { toast } from 'sonner'

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider: FC<AppProviderProps> = ({ children }) => {
  const { language, theme } = useAppStore()

  // Initialize App
  useAppInitialization()

  // Apply Theme & Language
  useEffect(() => {
    const root = window.document.documentElement
    root.lang = language

    const applyTheme = (t: string) => {
      root.classList.remove('light', 'dark')
      let effectiveTheme = t
      if (t === 'system') {
        effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light'
      }
      root.classList.add(effectiveTheme)

      // Sync meta theme-color with current theme for status bar & mobile chrome
      const metaThemeColor = document.querySelector('meta[name="theme-color"]')
      if (metaThemeColor) {
        metaThemeColor.setAttribute('content', effectiveTheme === 'dark' ? '#0D0E12' : '#F9FAFB')
      }
    }

    applyTheme(theme)
  }, [theme, language])

  // Global Error Handlers
  useEffect(() => {
    const handleGlobalError = (event: ErrorEvent | PromiseRejectionEvent) => {
      const msg =
        (event instanceof ErrorEvent ? event.error?.message : event.reason?.message) ||
        'Что-то пошло не так'
      if (msg.includes('ResizeObserver')) return
      toast.error(msg)
    }
    window.addEventListener('error', handleGlobalError)
    window.addEventListener('unhandledrejection', handleGlobalError)
    return () => {
      window.removeEventListener('error', handleGlobalError)
      window.removeEventListener('unhandledrejection', handleGlobalError)
    }
  }, [])

  return <>{children}</>
}
