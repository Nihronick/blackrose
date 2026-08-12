import { type FC, type ReactNode, createContext, useContext, useEffect, useState } from 'react'

export type AppEnvironment = {
  isTMA: boolean
  isInTelegram: boolean
  platform: string
  version: string
  colorScheme: 'light' | 'dark'
}

const AppEnvContext = createContext<AppEnvironment | null>(null)

export const detectEnvironment = (): AppEnvironment => {
  const w = typeof window !== 'undefined' ? (window as unknown as Record<string, unknown>) : {}
  const tg = (
    w.Telegram as
      | {
          WebApp?: {
            initData?: string
            platform?: string
            version?: string
            colorScheme?: 'light' | 'dark'
          }
        }
      | undefined
  )?.WebApp

  const loc = typeof window !== 'undefined' ? window.location : { hash: '', search: '' }
  const hasInitData = Boolean(
    (tg?.initData && tg.initData.length > 0) ||
      loc.hash.includes('tgWebAppData') ||
      loc.search.includes('tgWebAppData') ||
      loc.hash.includes('tgWebAppVersion') ||
      loc.search.includes('tgWebAppVersion')
  )

  const isTMA = Boolean(tg || hasInitData || w.TelegramWebviewProxy || w.TelegramGameProxy)

  const prefersDark =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches

  return {
    isTMA: isTMA,
    isInTelegram: isTMA,
    platform: tg?.platform || 'web',
    version: tg?.version || '8.0',
    colorScheme: tg?.colorScheme || (prefersDark ? 'dark' : 'light'),
  }
}

interface AppEnvProviderProps {
  children: ReactNode
}

export const AppEnvProvider: FC<AppEnvProviderProps> = ({ children }) => {
  const [env, setEnv] = useState<AppEnvironment>(detectEnvironment)

  useEffect(() => {
    // Re-evaluate environment after mount to catch async script injection
    setEnv(detectEnvironment())

    const t1 = setTimeout(() => setEnv(detectEnvironment()), 100)
    const t2 = setTimeout(() => setEnv(detectEnvironment()), 500)

    document.documentElement.classList.add('env-web')
    return () => {
      clearTimeout(t1)
      clearTimeout(t2)
      document.documentElement.classList.remove('env-web')
    }
  }, [])

  return <AppEnvContext.Provider value={env}>{children}</AppEnvContext.Provider>
}

export const useAppEnv = () => {
  const context = useContext(AppEnvContext)
  if (!context) return detectEnvironment()
  return context
}
