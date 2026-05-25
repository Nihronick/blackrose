import type { Category } from '@/features/categories'
import { create } from 'zustand'

export type Theme = 'light' | 'dark' | 'system'
export type AppLanguage = 'en' | 'ru'

export interface AppState {
  accessMsg: string | null
  isAdmin: boolean
  showQN: boolean
  cats: Category[]
  theme: Theme
  language: AppLanguage
  searchOpen: boolean
  hasOnboarded: boolean

  setSearchOpen: (open: boolean) => void
  setAccessMsg: (accessMsg: string | null) => void
  setIsAdmin: (isAdmin: boolean) => void
  setShowQN: (showQN: boolean) => void
  setCats: (cats: Category[]) => void
  setAccessDenied: (msg: string) => void
  setTheme: (theme: Theme) => void
  setLanguage: (language: AppLanguage) => void
  completeOnboarding: () => void
}

const VALID_THEMES: Theme[] = ['light', 'dark', 'system']
const VALID_LANGS: AppLanguage[] = ['en', 'ru']

function getStoredTheme(): Theme {
  try {
    const v = localStorage.getItem('br_theme') as Theme
    return VALID_THEMES.includes(v) ? v : 'system'
  } catch {
    return 'system'
  }
}

function getStoredLanguage(): AppLanguage {
  try {
    const v = localStorage.getItem('br_lang') as AppLanguage
    return VALID_LANGS.includes(v) ? v : 'ru'
  } catch {
    return 'ru'
  }
}

export const useAppStore = create<AppState>((set) => ({
  accessMsg: null,
  isAdmin: false,
  showQN: false,
  cats: [],
  theme: getStoredTheme(),
  language: getStoredLanguage(),
  searchOpen: false,
  hasOnboarded: localStorage.getItem('br_onboarded') === 'true',

  setSearchOpen: (searchOpen) => set({ searchOpen }),
  setAccessMsg: (accessMsg) => set({ accessMsg }),
  setIsAdmin: (isAdmin) => set({ isAdmin }),
  setShowQN: (showQN) => set({ showQN }),
  setCats: (cats) =>
    set((state) => {
      const same =
        state.cats.length === cats.length &&
        state.cats.every((cat, i) => {
          const next = cats[i]
          return (
            cat.key === next?.key &&
            cat.title === next?.title &&
            cat.icon === next?.icon &&
            cat.count === next?.count
          )
        })

      return same ? state : { cats }
    }),
  setAccessDenied: (msg) => set({ accessMsg: msg }),
  setTheme: (theme) => {
    localStorage.setItem('br_theme', theme)
    set({ theme })
  },
  setLanguage: (language) => {
    localStorage.setItem('br_lang', language)
    set({ language })
  },
  completeOnboarding: () => {
    localStorage.setItem('br_onboarded', 'true')
    set({ hasOnboarded: true })
  },
}))
