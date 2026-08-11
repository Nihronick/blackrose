import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merges class names using tailwind-merge and clsx.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Returns the correct plural form of a word based on the count (Russian logic).
 */
export function pluralize(n: number, one: string, few: string, many: string) {
  const m10 = n % 10
  const m100 = n % 100
  if (m100 >= 11 && m100 <= 19) return many
  if (m10 === 1) return one
  if (m10 >= 2 && m10 <= 4) return few
  return many
}

/**
 * Parses video URLs (YouTube or direct files).
 */
export function parseVideo(url: string | null) {
  if (!url) return null
  const yt = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
  if (yt) return { type: 'youtube' as const, id: yt[1] }
  if (url.match(/\.(mp4|webm|ogg|mov|m4v)(\?|$)/i)) return { type: 'video' as const, url }
  return { type: 'link' as const, url }
}

/**
 * Normalizes URLs, specifically handling GitHub links to point to jsDelivr or raw content.
 * jsDelivr is used for better performance and reliability in different regions.
 */
export function normalizeUrl(url: string | null | undefined): string {
  if (!url || typeof url !== 'string') return url || ''

  // Backend permanent media URLs (/api/media/...)
  if (url.startsWith('/api/media/') || url.startsWith('api/media/')) {
    const apiBase = (
      import.meta.env.VITE_API_URL || 'https://nihronick-blackrose-backend.hf.space'
    ).replace(/\/$/, '')
    const path = url.startsWith('/') ? url : `/${url}`
    return `${apiBase}${path}`
  }

  // Old guide media links may still point to jsDelivr gh-pages snapshot.
  // Prefer local public assets to avoid CDN blocks (403/ORB) and keep paths deploy-stable.
  const legacyCdnPrefix = 'https://cdn.jsdelivr.net/gh/Nihronick/blackrose@gh-pages/assets/'
  if (url.startsWith(legacyCdnPrefix)) {
    return `/assets/${url.slice(legacyCdnPrefix.length)}`
  }

  // Local assets from markdown (./assets/... / assets/...) should resolve correctly on GitHub Pages
  if (url.startsWith('./assets/') || url.startsWith('assets/')) {
    if (typeof window !== 'undefined') {
      return new URL(url, window.location.href).toString()
    }
    return `/${url.replace(/^\.\//, '')}`
  }

  // Already normalized?
  if (url.includes('cdn.jsdelivr.net')) return url

  // Support for GitHub Raw -> jsDelivr CDN
  if (url.includes('github.com') || url.includes('raw.githubusercontent.com')) {
    let path = url
    if (url.includes('github.com')) {
      path = url
        .replace(/^https?:\/\/(www\.)?github\.com/, '')
        .replace('/blob/', '/')
        .replace('/raw/', '/')
    } else {
      path = url.replace(/^https?:\/\/raw\.githubusercontent\.com/, '')
    }

    const parts = path.split('/').filter(Boolean)
    if (parts.length >= 3) {
      const user = parts[0]
      const repo = parts[1]
      const branch = parts[2]
      const rest = parts.slice(3).join('/')
      return `https://cdn.jsdelivr.net/gh/${user}/${repo}@${branch}/${rest}`
    }
  }

  return url
}

/**
 * Parses document URLs to extract name, extension and a simple emoji icon.
 */
export function parseDocument(url: string | null) {
  if (!url) return null
  const name = decodeURIComponent(url.split('/').pop()?.split('?')[0] || '') || 'Документ'
  const ext = name.split('.').pop()?.toLowerCase() || ''
  const icons: Record<string, string> = {
    pdf: '📕',
    doc: '📘',
    docx: '📘',
    xls: '📊',
    xlsx: '📊',
    png: '🖼',
    jpg: '🖼',
    jpeg: '🖼',
  }
  return { name, ext, icon: icons[ext] || '📄', url }
}
