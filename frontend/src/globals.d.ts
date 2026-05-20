import type { HTMLAttributes } from 'react'

declare global {
  interface Window {
    Capacitor?: {
      getPlatform: () => string
      isNativePlatform: () => boolean
    }
  }

  namespace JSX {
    interface IntrinsicElements {
      'layui-button': HTMLAttributes<HTMLElement> & {
        type?: 'primary' | 'warm' | 'danger' | 'disabled' | 'outline' | 'default'
        size?: 'lg' | 'md' | 'sm' | 'xs'
        radius?: boolean | string
        class?: string
        style?: any
        onClick?: any
      }
      'layui-badge': HTMLAttributes<HTMLElement> & {
        color?: 'green' | 'blue' | 'orange' | 'red' | 'cyan' | 'black' | 'default'
        rim?: boolean | string
        class?: string
      }
      'layui-card': HTMLAttributes<HTMLElement> & {
        title?: string
        class?: string
      }
      'layui-progress': HTMLAttributes<HTMLElement> & {
        percent?: string
        color?: 'red' | 'orange' | 'green' | 'cyan' | 'blue'
        class?: string
      }
      'layui-timeline': HTMLAttributes<HTMLElement> & {
        class?: string
      }
      'layui-timeline-item': HTMLAttributes<HTMLElement> & {
        time?: string
        title?: string
        class?: string
      }
    }
  }
}
