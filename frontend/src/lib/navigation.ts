import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * SwiftUI-inspired Navigation system.
 * Centralizes all route definitions and provides a type-safe navigation hook.
 */

export type Route =
  | { type: 'home' }
  | { type: 'category'; id: string }
  | { type: 'guide'; id: string }
  | { type: 'tag'; tag: string }
  | { type: 'favorites' }
  | { type: 'history' }
  | { type: 'admin' }
  | { type: 'roadmap' }

export const useAppNavigation = () => {
  const navigate = useNavigate()

  const push = useCallback(
    (route: Route) => {
      switch (route.type) {
        case 'home':
          navigate('/')
          break
        case 'category':
          navigate(`/category/${route.id}`)
          break
        case 'guide':
          navigate(`/guide/${encodeURIComponent(route.id)}`)
          break
        case 'tag':
          navigate(`/tag/${encodeURIComponent(route.tag)}`)
          break
        case 'favorites':
          navigate('/favorites')
          break
        case 'history':
          navigate('/history')
          break
        case 'admin':
          navigate('/admin')
          break
        case 'roadmap':
          navigate('/roadmap')
          break
      }
    },
    [navigate]
  )

  const pop = useCallback(() => {
    navigate(-1)
  }, [navigate])

  return { push, pop }
}
