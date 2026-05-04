import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Mock Telegram WebApp
window.Telegram = {
  WebApp: {
    initData: 'test',
    initDataUnsafe: {},
    ready: vi.fn(),
    close: vi.fn(),
    expand: vi.fn(),
    headerColor: '#ffffff',
    backgroundColor: '#ffffff',
    secondaryBackgroundColor: '#f5f5f5',
    colorScheme: 'dark',
    isExpanded: false,
    isClosingConfirmationEnabled: false,
    viewportHeight: 600,
    viewportStableHeight: 600,
    header_color: '#ffffff',
    background_color: '#ffffff',
    contentSafeAreaInset: { top: 0, bottom: 0, left: 0, right: 0 },
    safeAreaInset: { top: 0, bottom: 0, left: 0, right: 0 },
    themeParams: {
      bg_color: '#ffffff',
      text_color: '#000000',
      hint_color: '#999999',
    },
    HapticFeedback: {
      impactOccurred: vi.fn(),
      notificationOccurred: vi.fn(),
      selectionChanged: vi.fn(),
    },
    onEvent: vi.fn(),
    offEvent: vi.fn(),
    sendData: vi.fn(),
    setHeaderColor: vi.fn(),
    setBackgroundColor: vi.fn(),
    BackButton: {
      show: vi.fn(),
      hide: vi.fn(),
      onClick: vi.fn(),
      offClick: vi.fn(),
    },
    CloudStorage: {
      setItem: vi.fn(),
      getItem: vi.fn(),
      getItems: vi.fn(),
      removeItem: vi.fn(),
      removeItems: vi.fn(),
      getKeys: vi.fn(),
    },
  },
} as unknown as NonNullable<Window['Telegram']>
