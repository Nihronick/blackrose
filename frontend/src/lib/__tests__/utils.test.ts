import { describe, it, expect } from 'vitest'
import { cn, pluralize, parseVideo, normalizeUrl, parseDocument } from '../utils'

describe('cn - className merger', () => {
  it('merges simple class names', () => {
    expect(cn('px-2', 'py-4')).toBe('px-2 py-4')
  })

  it('removes duplicate tailwind classes', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4')
  })

  it('handles conditional classes', () => {
    const isActive = true
    expect(cn('base', isActive && 'active')).toContain('base')
    expect(cn('base', isActive && 'active')).toContain('active')
  })

  it('handles arrays of classes', () => {
    expect(cn(['px-2', 'py-4'])).toContain('px-2')
    expect(cn(['px-2', 'py-4'])).toContain('py-4')
  })

  it('handles undefined and null', () => {
    expect(cn('base', undefined, null, 'text')).toContain('base')
    expect(cn('base', undefined, null, 'text')).toContain('text')
  })
})

describe('pluralize - Russian pluralization', () => {
  it('uses "one" form for 1', () => {
    expect(pluralize(1, 'гайд', 'гайда', 'гайдов')).toBe('гайд')
  })

  it('uses "few" form for 2-4', () => {
    expect(pluralize(2, 'гайд', 'гайда', 'гайдов')).toBe('гайда')
    expect(pluralize(3, 'гайд', 'гайда', 'гайдов')).toBe('гайда')
    expect(pluralize(4, 'гайд', 'гайда', 'гайдов')).toBe('гайда')
  })

  it('uses "many" form for 0, 5-20, 25+', () => {
    expect(pluralize(0, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
    expect(pluralize(5, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
    expect(pluralize(20, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
    expect(pluralize(25, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
  })

  it('uses "many" form for 11-19', () => {
    expect(pluralize(11, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
    expect(pluralize(15, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
    expect(pluralize(19, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
  })

  it('works with large numbers', () => {
    expect(pluralize(101, 'гайд', 'гайда', 'гайдов')).toBe('гайд')
    expect(pluralize(102, 'гайд', 'гайда', 'гайдов')).toBe('гайда')
    expect(pluralize(111, 'гайд', 'гайда', 'гайдов')).toBe('гайдов')
  })
})

describe('parseVideo - video URL parsing', () => {
  it('returns null for empty/null input', () => {
    expect(parseVideo(null)).toBeNull()
    expect(parseVideo('')).toBeNull()
  })

  it('parses YouTube URLs', () => {
    const youtubeTests = [
      'https://youtube.com/watch?v=dQw4w9WgXcQ',
      'https://youtu.be/dQw4w9WgXcQ',
      'https://www.youtube.com/embed/dQw4w9WgXcQ',
    ]

    youtubeTests.forEach((url) => {
      const result = parseVideo(url)
      expect(result?.type).toBe('youtube')
      expect(result?.id).toBe('dQw4w9WgXcQ')
    })
  })

  it('parses video file URLs', () => {
    const videoTests = [
      'https://example.com/video.mp4',
      'https://example.com/video.webm',
      'https://example.com/video.ogg',
      'https://example.com/video.mov',
      'https://example.com/video.m4v',
    ]

    videoTests.forEach((url) => {
      const result = parseVideo(url)
      expect(result?.type).toBe('video')
      expect(result?.url).toBe(url)
    })
  })

  it('returns link type for other URLs', () => {
    const result = parseVideo('https://example.com/page')
    expect(result?.type).toBe('link')
    expect(result?.url).toBe('https://example.com/page')
  })

  it('handles query parameters in video URLs', () => {
    const result = parseVideo('https://example.com/video.mp4?quality=hd')
    expect(result?.type).toBe('video')
  })
})

describe('normalizeUrl - URL normalization', () => {
  it('returns empty string for null/undefined', () => {
    expect(normalizeUrl(null)).toBe('')
    expect(normalizeUrl(undefined)).toBe('')
  })

  it('converts legacy cdn.jsdelivr.net paths to local /assets', () => {
    const url = 'https://cdn.jsdelivr.net/gh/Nihronick/blackrose@gh-pages/assets/icons/some-icon.png'
    expect(normalizeUrl(url)).toBe('/assets/icons/some-icon.png')
  })

  it('normalizes local ./assets/ paths', () => {
    const result = normalizeUrl('./assets/image.png')
    expect(result).toContain('assets/image.png')
  })

  it('normalizes local assets/ paths', () => {
    const result = normalizeUrl('assets/image.png')
    expect(result).toContain('assets/image.png')
  })

  it('leaves cdn.jsdelivr.net URLs unchanged', () => {
    const url = 'https://cdn.jsdelivr.net/gh/user/repo@main/file.png'
    expect(normalizeUrl(url)).toBe(url)
  })

  it('converts GitHub URLs to cdn.jsdelivr.net', () => {
    const ghUrl = 'https://github.com/user/repo/blob/main/file.png'
    expect(normalizeUrl(ghUrl)).toContain('cdn.jsdelivr.net/gh/user/repo@main/file.png')
  })

  it('converts raw.githubusercontent.com URLs to cdn.jsdelivr.net', () => {
    const rawUrl = 'https://raw.githubusercontent.com/user/repo/main/file.png'
    expect(normalizeUrl(rawUrl)).toContain('cdn.jsdelivr.net/gh/user/repo@main/file.png')
  })

  it('returns URL unchanged if no normalization needed', () => {
    const url = 'https://example.com/image.png'
    expect(normalizeUrl(url)).toBe(url)
  })

  it('handles non-string input gracefully', () => {
    const result = normalizeUrl(123 as any)
    // The function returns the input if it's not a string
    expect(typeof result === 'string' || typeof result === 'number').toBe(true)
  })
})

describe('parseDocument - document URL parsing', () => {
  it('returns null for empty/null input', () => {
    expect(parseDocument(null)).toBeNull()
  })

  it('extracts document name and extension', () => {
    const result = parseDocument('https://example.com/my-document.pdf')
    expect(result?.name).toBe('my-document.pdf')
    expect(result?.ext).toBe('pdf')
  })

  it('returns correct emoji icons for extensions', () => {
    const tests = [
      { ext: 'pdf', icon: '📕', url: 'https://example.com/doc.pdf' },
      { ext: 'doc', icon: '📘', url: 'https://example.com/file.doc' },
      { ext: 'docx', icon: '📘', url: 'https://example.com/file.docx' },
      { ext: 'xls', icon: '📊', url: 'https://example.com/data.xls' },
      { ext: 'xlsx', icon: '📊', url: 'https://example.com/data.xlsx' },
      { ext: 'png', icon: '🖼', url: 'https://example.com/image.png' },
      { ext: 'jpg', icon: '🖼', url: 'https://example.com/image.jpg' },
    ]

    tests.forEach(({ url, icon, ext }) => {
      const result = parseDocument(url)
      expect(result?.icon).toBe(icon)
      expect(result?.ext).toBe(ext)
    })
  })

  it('returns default icon for unknown extensions', () => {
    const result = parseDocument('https://example.com/archive.zip')
    expect(result?.icon).toBe('📄')
  })

  it('handles URLs with query parameters', () => {
    const result = parseDocument('https://example.com/document.pdf?v=1&token=abc')
    expect(result?.name).toBe('document.pdf')
    expect(result?.ext).toBe('pdf')
  })

  it('decodes URL-encoded names', () => {
    const result = parseDocument('https://example.com/My%20Document.pdf')
    expect(result?.name).toBe('My Document.pdf')
  })

  it('defaults to "Документ" when no name found', () => {
    const result = parseDocument('https://example.com/')
    expect(result?.name).toBe('Документ')
  })
})
