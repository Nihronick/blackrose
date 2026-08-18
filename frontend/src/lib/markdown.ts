// @ts-nocheck
import DOMPurify from 'dompurify'
import { type RendererExtension, type TokenizerExtension, type Tokens, marked } from 'marked'
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
  renderer(token: Tokens.Generic): string {
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
    heading({ text, depth }: Tokens.Heading) {
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
    blockquote({ tokens }: Tokens.Blockquote) {
      const body = marked.parser(tokens ?? [])
      return `<blockquote class="guide-quote">${body}</blockquote>`
    },
    // li с классом (ul/ol различаем через ordered)
    listitem({ tokens, task }: Tokens.ListItem) {
      const text = marked.parser(tokens ?? [])
      if (task) return `<li class="guide-li guide-task">${text}</li>`
      return `<li class="guide-li">${text}</li>`
    },
    list(
      this: { listitem?: (item: Tokens.ListItem) => string } | undefined,
      { items, ordered }: Tokens.List
    ) {
      const itemsHtml = (items || [])
        .map((item: Tokens.ListItem) => this.listitem?.(item) ?? '')
        .join('')
      const cls = ordered ? 'guide-ol' : 'guide-ul'
      const tag = ordered ? 'ol' : 'ul'
      // Добавляем класс на каждый li
      const withClass = (itemsHtml || '').replace(
        /<li class="guide-li"/g,
        `<li class="guide-li ${cls}"`
      )
      return `<${tag}>${withClass}</${tag}>`
    },
    // HR с классом
    hr() {
      return '<hr class="guide-hr">'
    },
    // Код с классом
    codespan({ text }: Tokens.Codespan) {
      const codeText = text ?? ''
      return `<code class="guide-code">${codeText}</code>`
    },
    // Внешние ссылки — target=_blank + rel=noreferrer
    link(...args: unknown[]) {
      const first = args[0]
      const href =
        typeof first === 'string'
          ? first
          : typeof first === 'object' && first !== null && 'href' in first
            ? String((first as { href?: unknown }).href ?? '')
            : ''
      const text =
        typeof first === 'string'
          ? typeof args[2] === 'string'
            ? args[2]
            : href
          : typeof first === 'object' && first !== null && 'text' in first
            ? String((first as { text?: unknown }).text ?? '')
            : ''

      const normalizedHref = normalizeUrl(href ?? '')
      const label = text || normalizedHref

      // Специальная обработка для [Video: name](url), [Видео: name](url) и прямых ссылок на видео
      const isVideoLabel =
        label.toLowerCase().includes('video') ||
        label.toLowerCase().includes('видео') ||
        label.toLowerCase().includes('инструкция')
      const isVideoExt = /\.(mp4|webm|mov|avi)($|\?)/i.test(normalizedHref)
      const isApiMediaVideo =
        normalizedHref.includes('/api/media/') &&
        (isVideoLabel || label === normalizedHref || isVideoExt)

      if (
        isVideoLabel ||
        isVideoExt ||
        isApiMediaVideo ||
        normalizedHref.includes('youtube.com') ||
        normalizedHref.includes('youtu.be')
      ) {
        const isYoutube =
          normalizedHref.includes('youtube.com') || normalizedHref.includes('youtu.be')
        const embedUrl = isYoutube
          ? normalizedHref.replace('watch?v=', 'embed/').replace('youtu.be/', 'youtube.com/embed/')
          : normalizedHref

        if (isYoutube) {
          return (
            '<div class="my-6 rounded-2xl overflow-hidden border border-rose-500/20 bg-black/90 aspect-video shadow-2xl">' +
            `<iframe src="${embedUrl}" title="Video" class="w-full h-full border-0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>` +
            '</div>'
          )
        }

        return (
          '<div class="my-6 rounded-2xl overflow-hidden border border-rose-500/20 bg-black/90 aspect-video shadow-2xl">' +
          `<video src="${normalizedHref}" controls preload="metadata" class="w-full h-full object-cover"></video>` +
          '</div>'
        )
      }

      const isExternal = normalizedHref.includes('://') || normalizedHref.startsWith('//')
      if (isExternal) {
        return `<a href="${normalizedHref}" target="_blank" rel="noreferrer" class="guide-extlink hover:text-primary transition-colors underline decoration-primary/30 underline-offset-4">${label}</a>`
      }
      return `<a href="${normalizedHref}" class="text-primary hover:underline">${label}</a>`
    },
    // Изображения с нормализацией GitHub и no-referrer
    image(...args: unknown[]) {
      const first = args[0]
      const href =
        typeof first === 'string'
          ? first
          : typeof first === 'object' && first !== null && 'href' in first
            ? String((first as { href?: unknown }).href ?? '')
            : ''
      const text =
        typeof first === 'string'
          ? typeof args[2] === 'string'
            ? args[2]
            : ''
          : typeof first === 'object' && first !== null && 'text' in first
            ? String((first as { text?: unknown }).text ?? '')
            : ''
      const src = normalizeUrl(href ?? '')
      const alt = text ?? ''
      const isVid = /\.(mp4|webm|mov|avi)($|\?)/i.test(src)
      if (isVid) {
        return (
          '<div class="my-6 rounded-2xl overflow-hidden border border-rose-500/20 bg-black/90 aspect-video shadow-2xl">' +
          `<video src="${src}" controls preload="metadata" class="w-full h-full object-cover"></video>` +
          '</div>'
        )
      }
      return (
        '<div class="my-6 flex flex-col items-center justify-center">' +
        `<img src="${src}" alt="${alt}" class="guide-img rounded-2xl border border-rose-500/20 shadow-xl max-h-[550px] w-auto object-contain cursor-pointer hover:scale-[1.01] transition-transform duration-300" loading="lazy" referrerpolicy="no-referrer">` +
        (alt && alt !== 'Скриншот'
          ? `<p class="text-[11px] text-rose-300/80 mt-2 text-center italic">${alt}</p>`
          : '') +
        '</div>'
      )
    },
  },
})

// ── Иконки {{ICON_NAME}} ──────────────────────────────────────

function replaceIcons(text: string, iconResolver: (name: string) => string) {
  // Clean up any untranslated placeholders like __CODE21__ or КОД29 or XZYBLOCK29XZY
  const cleanText = text
    .replace(/__(?:CODE|КОД)\d+__/gi, '')
    .replace(/XZYBLOCK\d+XZY/gi, '')
    .replace(/КОД\d+/gi, '')

  return cleanText.replace(/\{\{([^{}]+)\}\}/g, (_, rawName) => {
    const name = String(rawName || '').trim()
    if (!name) return ''

    if (/^https?:\/\//i.test(name) || name.startsWith('/api/media/') || name.startsWith('api/media/')) {
      const normalized = normalizeUrl(name)
      return `<img src="${normalized}" alt="icon" title="icon" class="inline-icon" width="20" height="20" style="display:inline-block;vertical-align:middle;margin:0 3px;cursor:pointer;">`
    }

    const cleanName = name.replace(/^icon:/i, '').trim()
    const url = iconResolver(cleanName) || iconResolver(name)
    if (!url) {
      return `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-rose-500/10 text-rose-300 border border-rose-500/20 text-[11px] font-semibold mx-0.5 select-none" data-icon-name="${cleanName}" style="display:inline-flex;vertical-align:middle;">✨ ${cleanName}</span>`
    }
    return `<img src="${url}" alt="${cleanName}" title="${cleanName}" data-icon-name="${cleanName}" class="inline-icon" width="20" height="20" style="display:inline-block;vertical-align:middle;margin:0 3px;cursor:pointer;">`
  })
}

// ── Guide cyberlinks [[key]] и [[key|Подпись]] ────────────────

function replaceCyberlinks(
  text: string,
  guideLinks: Record<string, { title?: string; icon?: string }> = {}
) {
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
      return `{{https://cdn.discordapp.com/emojis/${id}.webp?size=48&quality=lossless}}`
    })
    .replace(/(^|[^\w]):([A-Za-z][A-Za-z0-9_]*):(?!\/\/)/g, '$1{{$2}}')
}

// ── DOMPurify конфиг ──────────────────────────────────────────

const PURIFY_CONFIG = {
  ALLOWED_TAGS: [
    'div',
    'p',
    'details',
    'summary',
    'strong',
    'em',
    's',
    'u',
    'code',
    'h2',
    'h3',
    'h4',
    'blockquote',
    'li',
    'ol',
    'ul',
    'a',
    'img',
    'video',
    'iframe',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
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
    'allow',
    'allowfullscreen',
    'frameborder',
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
