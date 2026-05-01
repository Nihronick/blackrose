import { useCallback, useState } from 'react'

/**
 * SwiftUI-inspired Sheet manager.
 * Replaces multiple boolean flags with a single 'activeItem' state.
 */

export function useSheet<T>() {
  const [activeItem, setActiveItem] = useState<T | null>(null)

  const present = useCallback((item: T) => {
    setActiveItem(item)
  }, [])

  const dismiss = useCallback(() => {
    setActiveItem(null)
  }, [])

  return {
    item: activeItem,
    present,
    dismiss,
    isPresented: activeItem !== null,
  }
}
