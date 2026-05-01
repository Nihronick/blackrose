import DOMPurify from 'dompurify'
import { marked, type TokenizerExtension, type RendererExtension } from 'marked'
import { normalizeUrl, parseVideo } from './utils'

/**
 * Форматтер гайдов — порт Python format_guide_text на JS.
 *
 * Порядок обработки:
 * 1. {{ICON}} → <img class="inline-icon">
 * 2. [[guide_key]] и [[guide_key|Подпись]] → <a class="guide-cyberlink">
 * 3. marked.js парсит стандартный Markdown (**, *, ~~, `code`, #, >, -, 1.)
 * 4. DOMPurify санитизирует HTML
 */

// ── Кастомные токены marked.js ────────────────────────────────

interface SpoilerToken {
  type: 'spoiler'
  raw: string
  text: string
}

/** Токен для ||спойлер|| */
const spoilerExtension: TokenizerExtension & RendererExtension = {
  name: 'spoiler',
  level: 'inline',
  start: (src: string) => src.indexOf('||'),
  tokenizer(src: string): SpoilerToken | undefined {
    const match = src.match(/^\|\|(.+?)\|\|/)
    if (match) return { type: 'spoiler', raw: match[0], text: match[1] }
  },
  renderer(token: any): string {
    return `<span class="guide-spoiler">${token.text}</span>`
  },
}

marked.use({ extensions: [spoilerExtension] })

// ── Настройка marked ──────────────────────────────────────────

marked.use({
  breaks: true, // \n → <br>
  gfm: true, // GitHub Flavored Markdown
  renderer: {
    // Заголовки с классами
    heading({ text, depth }: any) {
      const headerText = text ?? ''
      const level = depth ?? 2
      // Simple slugify for IDs
      const id = headerText
        .toLowerCase()
        .replace(/[^\wа-яё\s]/gi, '')
        .replace(/\s+/g, '-')
        .trim()

      if (level === 2) return `<h2 id="${id}" class="guide-h2">${headerText}</h2>`
      if (level === 3) return `<h3 id="${id}" class="guide-h3">${headerText}</h3>`
      return `<h${level} id="${id}">${headerText}</h${level}>`
    },
    // Blockquote с классом
    blockquote({ tokens }: any) {
      const body = marked.parser(tokens ?? [])
      return `<blockquote class="guide-quote">${body}</blockquote>`
    },
    // li с классом (ul/ol различаем через ordered)
    listitem({ tokens, task }: any) {
      const text = marked.parser(tokens ?? [])
      if (task) return `<li class="guide-li guide-task">${text}</li>`
      return `<li class="guide-li">${text}</li>`
    },
    list({ items, ordered }: any) {
      const itemsHtml = (items || []).map((item: any) => this.listitem?.(item) ?? '').join('')
      const cls = ordered ? 'guide-ol' : 'guide-ul'
      const tag = ordered ? 'ol' : 'ul'
      // Добавляем класс на каждый li
      const withClass = (itemsHtml || '').replace(/<li class="guide-li"/g, `<li class="guide-li ${cls}"`)
      return `<${tag}>${withClass}</${tag}>`
    },
    // HR с классом
    hr() {
      return '<hr class="guide-hr">'
    },
    // Код с классом
    codespan({ text }: any) {
      const codeText = text ?? ''
      return `<code class="guide-code">${codeText}</code>`
    },
    // Внешние ссылки — target=_blank + rel=noreferrer
    link({ href, title, tokens }: any) {
      const normalizedHref = normalizeUrl(href ?? '')
      const label = tokens ? marked.parser(tokens) : ''

      // Специальная обработка для [Video: name](url)
      if (typeof label === 'string' && label.includes('Video:')) {
        return `<div class="premium-video-placeholder my-6" data-video-url="${normalizedHref}" data-video-alt="${label.replace('Video:', '').trim()}"></div>`
      }

      if (normalizedHref.startsWith('http')) {
        return `<a href="${normalizedHref}" target="_blank" rel="noreferrer" class="guide-extlink hover:text-primary transition-colors underline decoration-primary/30 underline-offset-4">${label}</a>`
      }
      return `<a href="${normalizedHref}" class="text-primary hover:underline">${label}</a>`
    },
    // Изображения с нормализацией GitHub и no-referrer
    image({ href, title, text }: any) {
      const src = normalizeUrl(href ?? '')
      const alt = text ?? ''
      const parsedVideo = parseVideo(src)
      if (parsedVideo?.type === 'video') {
        return `<div class="premium-video-placeholder my-6" data-video-url="${src}" data-video-alt="${alt}"></div>`
      }
      return (
        '<div class="my-6">' +
        `<img src="${src}" alt="${alt}" class="guide-img rounded-2xl border border-border/30 shadow-xl" loading="lazy" referrerpolicy="no-referrer">` +
        (alt
          ? `<p class="text-[11px] text-muted-foreground mt-2 text-center italic">${alt}</p>`
          : '') +
        '</div>'
      )
    },
  },
})

// ── Иконки {{ICON_NAME}} ──────────────────────────────────────

function replaceIcons(text: string, iconResolver: (name: string) => string) {
  return text.replace(/\{\{([^{}]+)\}\}/g, (_, rawName) => {
    const name = String(rawName || '').trim()
    if (!name) return ''

    if (/^https?:\/\//i.test(name)) {
      const normalized = normalizeUrl(name)
      return `<img src="${normalized}" alt="icon" title="icon" class="inline-icon" width="20" height="20" style="vertical-align:middle;margin:0 4px;cursor:pointer;">`
    }

    const url = iconResolver(name)
    if (!url) {
      return `<span class="px-1.5 py-0.5 rounded-md bg-muted/50 text-[10px] font-bold text-muted-foreground border border-border/50 inline-flex items-center gap-1 leading-none mx-0.5 select-none" data-icon-name="${name}" style="vertical-align:middle;cursor:help;">⚠️ ${name}</span>`
    }
    return `<img src="${url}" alt="${name}" title="${name}" data-icon-name="${name}" class="inline-icon" width="20" height="20" style="vertical-align:middle;margin:0 4px;cursor:pointer;">`
  })
}

// ── Guide cyberlinks [[key]] и [[key|Подпись]] ────────────────

function replaceCyberlinks(text: string, guideLinks: Record<string, { title?: string; icon?: string }> = {}) {
  return text.replace(
    /\[\[([^\]|]+)(?:\|([^\]]*))?\]\]/g,
    (_: string, keyPart: string, labelPart: string) => {
      let key = keyPart.trim()
      let label = labelPart?.trim() ?? ''

      if (key.includes('|')) {
        const [k, l] = key.split('|', 2)
        key = k.trim()
        label = l.trim()
      }

      const info = guideLinks[key] ?? {}
      const title = info.title ?? key
      const icon = info.icon ?? ''
      const display = label || title

      const iconHtml = icon
        ? `<img src="${icon}" width="16" height="16" style="vertical-align:middle;margin-right:4px;border-radius:3px;">`
        : ''

      return (
        `<a class="guide-cyberlink" data-guide-key="${key}" ` +
        `data-guide-title="${title}" data-guide-icon="${icon}" href="#">` +
        `${iconHtml}${display}` +
        `<svg class="guide-cyberlink-arrow" viewBox="0 0 16 16" width="12" height="12" ` +
        `fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" ` +
        `style="margin-left:4px;vertical-align:middle">` +
        `<path d="M3 8h10M9 4l4 4-4 4"/></svg></a>`
      )
    }
  )
}

function normalizeDiscordMarkdown(text: string, iconResolver: (name: string) => string): string {
  return text
    .replace(/^-#\s?/gm, '')
    .replace(/<a?:([A-Za-z0-9_]+):(\d{17,19})>/g, (_m, name, id) => {
      const byName = iconResolver(name) ? name : ''
      if (byName) return `{{${byName}}}`
      return `{{icon_${id}}}`
    })
    .replace(/(^|[^\w]):([A-Za-z][A-Za-z0-9_]*):(?!\/\/)/g, '$1{{$2}}')
}

// ── DOMPurify конфиг ──────────────────────────────────────────

const PURIFY_CONFIG = {
  ALLOWED_TAGS: [
    'div',
    'strong',
    'em',
    's',
    'u',
    'code',
    'h2',
    'h3',
    'blockquote',
    'li',
    'ol',
    'ul',
    'a',
    'img',
    'video',
    'br',
    'hr',
    'span',
    'svg',
    'path',
  ],
  ALLOWED_ATTR: [
    'href',
    'target',
    'rel',
    'class',
    'src',
    'alt',
    'title',
    'width',
    'height',
    'style',
    'loading',
    'controls',
    'preload',
    'referrerpolicy',
    'viewBox',
    'fill',
    'stroke',
    'stroke-width',
    'stroke-linecap',
    'd',
    'data-guide-key',
    'data-guide-title',
    'data-guide-icon',
    'data-icon-name',
    'data-video-url',
    'data-video-alt',
    'id',
  ],
  FORCE_BODY: false,
}

// ── Главная функция ───────────────────────────────────────────

interface FormatOptions {
  guideLinks?: Record<string, { title?: string; icon?: string }>
  iconResolver?: (name: string) => string
}

/**
 * formatGuideText(rawMarkdown, { guideLinks, iconResolver })
 *
 * @param raw — сырой markdown из БД
 * @param options — { guideLinks, iconResolver }
 * @returns — безопасный HTML
 */
export function formatGuideText(raw: string, options: FormatOptions = {}): string {
  const { guideLinks = {}, iconResolver = () => '' } = options
  if (!raw) return ''

  // 1. Заменяем кастомный синтаксис ДО marked (иначе marked их поломает)
  let text = normalizeDiscordMarkdown(raw, iconResolver)
  text = replaceIcons(text, iconResolver)
  text = replaceCyberlinks(text, guideLinks)

  // 2. marked.js парсит markdown
  const html = marked.parse(text) as string

  // 3. DOMPurify санитизирует
  return DOMPurify.sanitize(html, PURIFY_CONFIG)
}
