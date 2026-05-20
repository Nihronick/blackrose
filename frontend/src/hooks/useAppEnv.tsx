import { type FC, type ReactNode, createContext, useContext, useEffect, useState } from 'react'

export type AppEnvironment = {
  isTMA: false
  isInTelegram: false
  platform: 'web'
  version: string
  colorScheme: 'light' | 'dark'
}

const AppEnvContext = createContext<AppEnvironment | null>(null)

export const detectEnvironment = (): AppEnvironment => {
  const prefersDark =
    typeof window !== 'undefined' &&
    typeof window.matchMedia === 'function' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches

  return {
    isTMA: false,
    isInTelegram: false,
    platform: 'web',
    version: '1.0',
    colorScheme: prefersDark ? 'dark' : 'light',
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
