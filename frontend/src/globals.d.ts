import type React from 'react'
import type { HTMLAttributes } from 'react'

export interface TelegramWebApp {
  initData: string
  initDataUnsafe?: {
    query_id?: string
    user?: {
      id: number
      first_name: string
      last_name?: string
      username?: string
      language_code?: string
      is_premium?: boolean
    }
    auth_date?: string
    hash?: string
    start_param?: string
  }
  colorScheme: 'light' | 'dark'
  themeParams?: {
    bg_color?: string
    text_color?: string
    hint_color?: string
    link_color?: string
    button_color?: string
    button_text_color?: string
    secondary_bg_color?: string
  }
  isExpanded: boolean
  viewportHeight: number
  viewportStableHeight: number
  headerColor?: string
  backgroundColor?: string
  BackButton: {
    isVisible: boolean
    show: () => void
    hide: () => void
    onClick: (callback: () => void) => void
    offClick: (callback: () => void) => void
  }
  MainButton: {
    text: string
    color: string
    textColor: string
    isVisible: boolean
    isActive: boolean
    isProgressVisible: boolean
    setText: (text: string) => void
    show: () => void
    hide: () => void
    enable: () => void
    disable: () => void
    showProgress: (leaveActive?: boolean) => void
    hideProgress: () => void
    onClick: (callback: () => void) => void
    offClick: (callback: () => void) => void
  }
  HapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void
    selectionChanged: () => void
  }
  expand: () => void
  close: () => void
  requestFullscreen?: () => void
  enableClosingConfirmation?: () => void
  disableClosingConfirmation?: () => void
  setHeaderColor?: (color: string) => void
  setBackgroundColor?: (color: string) => void
  ready: () => void
}

declare global {
  interface Window {
    Capacitor?: {
      getPlatform: () => string
      isNativePlatform: () => boolean
    }
    Telegram?: {
      WebApp?: TelegramWebApp
    }
  }
}
