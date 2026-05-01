export {}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: {
        ready: () => void
        expand: () => void
        close: () => void
        headerColor: string
        backgroundColor: string
        themeParams: {
          bg_color?: string
          text_color?: string
          hint_color?: string
          link_color?: string
          button_color?: string
          button_text_color?: string
          secondary_bg_color?: string
          header_bg_color?: string
          accent_text_color?: string
          section_bg_color?: string
          section_header_text_color?: string
          subtitle_text_color?: string
          destructive_text_color?: string
        }
        HapticFeedback: {
          impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
          notificationOccurred: (type: 'error' | 'success' | 'warning') => void
          selectionChanged: () => void
        }
        onEvent: (event: string, callback: () => void) => void
        offEvent: (event: string, callback: () => void) => void
        sendData: (data: string) => void
        initData: string
        initDataUnsafe: {
          query_id?: string
          user?: {
            id: number
            first_name: string
            last_name?: string
            username?: string
            language_code?: string
            is_premium?: boolean
            photo_url?: string
          }
          receiver?: {
            id: number
            first_name: string
            last_name?: string
            username?: string
          }
          chat?: {
            id: number
            type: string
            title: string
            username?: string
            photo_url?: string
          }
          chat_type?: string
          chat_instance?: string
          start_param?: string
          can_send_after?: number
          auth_date: number
          hash: string
        }
        colorScheme: 'light' | 'dark'
        isExpanded: boolean
        viewportHeight: number
        viewportStableHeight: number
        headerColor: string
        backgroundColor: string
        secondaryBackgroundColor: string
        isClosingConfirmationEnabled: boolean
        header_color: string
        background_color: string
        contentSafeAreaInset: { top: number; bottom: number; left: number; right: number }
        safeAreaInset: { top: number; bottom: number; left: number; right: number }
        setHeaderColor: (color: string) => void
        setBackgroundColor: (color: string) => void
        BackButton: {
          show: () => void
          hide: () => void
          onClick: (cb: () => void) => void
          offClick: (cb: () => void) => void
        }
        CloudStorage: {
          setItem: (
            key: string,
            value: string,
            callback?: (err: Error | null, success: boolean) => void
          ) => void
          getItem: (
            key: string,
            callback: (err: Error | null, value: string | null) => void
          ) => void
          getItems: (
            keys: string[],
            callback: (err: Error | null, values: (string | null)[]) => void
          ) => void
          removeItem: (
            key: string,
            callback?: (err: Error | null, success: boolean) => void
          ) => void
          removeItems: (
            keys: string[],
            callback?: (err: Error | null, success: boolean) => void
          ) => void
          getKeys: (callback: (err: Error | null, keys: string[]) => void) => void
        }
      }
    }
    Capacitor?: {
      getPlatform: () => string
      isNativePlatform: () => boolean
    }
  }
}
