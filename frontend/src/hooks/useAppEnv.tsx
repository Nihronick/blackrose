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
  const tg =
    typeof window !== 'undefined'
      ? (
          window as unknown as {
            Telegram?: {
              WebApp?: {
                initData?: string
                platform?: string
                version?: string
                colorScheme?: 'light' | 'dark'
              }
            }
          }
        ).Telegram?.WebApp
      : undefined
  const hasInitData = Boolean(tg?.initData && tg.initData.length > 0)
  const isTMA = Boolean(tg && (hasInitData || (tg.platform && tg.platform !== 'unknown')))

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
  const [env] = useState<AppEnvironment>(detectEnvironment)

  useEffect(() => {
    document.documentElement.classList.add('env-web')
    return () => {
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
