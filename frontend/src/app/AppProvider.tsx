import { FC, ReactNode, useEffect } from 'react'
import { useAppStore } from '@/store'
import { useAppInitialization } from '@/hooks/useAppInitialization'
import { useAppEnv } from '@/hooks/useAppEnv'
import { toast } from 'sonner'

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider: FC<AppProviderProps> = ({ children }) => {
  const { isTMA, setIsTMA } = useAppEnv()
  const { language, theme, setIsTMA: setStoreIsTMA } = useAppStore()

  // Sync isTMA
  useEffect(() => {
    setStoreIsTMA(isTMA)
  }, [isTMA, setStoreIsTMA])

  // Initialize App
  useAppInitialization()

  // Apply Theme & Language
  useEffect(() => {
    const root = window.document.documentElement
    root.lang = language
    
    const applyTheme = (t: string) => {
      root.classList.remove('light', 'dark')
      if (t === 'system') {
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        root.classList.add(systemTheme)
      } else {
        root.classList.add(t)
      }
    }
    
    applyTheme(theme)
  }, [theme, language])

  // Global Error Handlers
  useEffect(() => {
    const handleGlobalError = (event: ErrorEvent | PromiseRejectionEvent) => {
      const msg = (event instanceof ErrorEvent ? event.error?.message : event.reason?.message) || 'Что-то пошло не так'
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
