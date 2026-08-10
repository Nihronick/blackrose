import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * SwiftUI-inspired Navigation system.
 * Centralizes all route definitions and provides a type-safe navigation hook.
 */

export type Route =
  | { type: 'home' }
  | { type: 'categories' }
  | { type: 'category'; id: string }
  | { type: 'guide'; id: string }
  | { type: 'tag'; tag: string }
  | { type: 'favorites' }
  | { type: 'history' }
  | { type: 'admin' }
  | { type: 'roadmap' }
  | { type: 'profile' }
  | { type: 'search' }
  | { type: 'guilds' }
  | { type: 'guild'; id: number }
  | { type: 'build' }

export const useAppNavigation = () => {
  const navigate = useNavigate()

  const safeNavigate = useCallback(
    (to: string | number) => {
      if (typeof document !== 'undefined' && 'startViewTransition' in document) {
        ;(
          document as unknown as { startViewTransition: (cb: () => void) => void }
        ).startViewTransition(() => {
          if (typeof to === 'number') {
            navigate(to)
          } else {
            navigate(to)
          }
        })
      } else {
        if (typeof to === 'number') {
          navigate(to)
        } else {
          navigate(to)
        }
      }
    },
    [navigate]
  )

  const push = useCallback(
    (route: Route) => {
      switch (route.type) {
        case 'home':
          safeNavigate('/')
          break
        case 'categories':
          safeNavigate('/categories')
          break
        case 'category':
          safeNavigate(`/category/${route.id}`)
          break
        case 'guide':
          safeNavigate(`/guide/${encodeURIComponent(route.id)}`)
          break
        case 'tag':
          safeNavigate(`/tag/${encodeURIComponent(route.tag)}`)
          break
        case 'favorites':
          safeNavigate('/favorites')
          break
        case 'history':
          safeNavigate('/history')
          break
        case 'admin':
          safeNavigate('/admin')
          break
        case 'roadmap':
          safeNavigate('/roadmap')
          break
        case 'profile':
          safeNavigate('/profile')
          break
        case 'search':
          safeNavigate('/search')
          break
        case 'guilds':
          safeNavigate('/guilds')
          break
        case 'guild':
          safeNavigate(`/guilds/${route.id}`)
          break
        case 'build':
          safeNavigate('/build')
          break
      }
    },
    [safeNavigate]
  )

  const pop = useCallback(() => {
    safeNavigate(-1)
  }, [safeNavigate])

  return { push, pop }
}
