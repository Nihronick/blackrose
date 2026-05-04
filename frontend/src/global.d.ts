export {}

declare global {
  interface TelegramUser {
    id: number
    first_name: string
    last_name?: string
    username?: string
    language_code?: string
    is_premium?: boolean
    photo_url?: string
  }

  interface Window {
    Telegram?: {
      WebApp: {
        ready: () => void
        expand: () => void
        close: () => void
        onEvent: (name: string, callback: () => void) => void
        offEvent: (name: string, callback: () => void) => void
        platform: string
        version: string
        colorScheme: 'light' | 'dark'
        initData: string
        initDataUnsafe?: {
          user?: TelegramUser
          query_id?: string
          auth_date?: string
          hash?: string
        }
      }
    }
  }
}
