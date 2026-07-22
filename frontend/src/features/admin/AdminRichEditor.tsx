import { apiUpload } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { Columns, Edit3, Eye, ImageIcon, Sparkles } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type { ChangeEvent, FC } from 'react'
import type React from 'react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { IconSheet } from './IconSheet'
import { MediaSheet } from './MediaSheet'
import RichEditorToolbar from './RichEditorToolbar'

function normalizeIcons(text: string): string {
  return text.replace(/:(\w+):/g, (_, k) => `{{${k}}}`)
}

function renderMd(text: string | null | undefined): string {
  if (!text || typeof text !== 'string') return ''
  try {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/~~(.*?)~~/g, '<s>$1</s>')
      .replace(
        /\|\|(.*?)\|\|/g,
        '<span class="bg-muted px-1 rounded text-transparent hover:text-inherit transition-colors">$1</span>'
      )
      .replace(/<u>(.*?)<\/u>/g, '<u>$1</u>')
      .replace(
        /`(.*?)`/g,
        '<code class="bg-muted/80 px-1 py-0.5 rounded font-mono text-[0.9em]">$1</code>'
      )
      .replace(/^### (.+)$/gm, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
      .replace(
        /^## (.+)$/gm,
        '<h2 class="text-xl font-extrabold mt-6 mb-3 border-b border-border/10 pb-1">$1</h2>'
      )
      .replace(
        /^> (.+)$/gm,
        '<blockquote class="border-l-4 border-primary/20 pl-4 py-1 my-3 text-muted-foreground italic bg-primary/5 rounded-r">$1</blockquote>'
      )
      .replace(/^- (.+)$/gm, '• $1')
      .replace(/^\d+\. (.+)$/gm, '1. $1')
      .replace(/\[(.+?)\]\((.*?)\)/g, '<a href="$2" class="text-primary hover:underline">$1</a>')
      .replace(
        /\[\[([^\]|]+)(?:\|([^\]]*))?\]\]/g,
        (_, key, label) =>
          `<span class="bg-blue-500/10 text-blue-500 px-1.5 py-0.5 rounded-md font-bold text-[0.9em] cursor-pointer hover:bg-blue-500/20 transition-all">${label || key}</span>`
      )
      .replace(
        /{{(\w+)}}/g,
        '<span class="inline-flex items-center justify-center p-1 bg-muted rounded font-bold text-xs">🖼 $1</span>'
      )
      .replace(
        /!\[(.*?)\]\((.*?)\)/g,
        (_, alt, url) =>
          `<div class="my-4 border border-border/20 rounded-xl overflow-hidden bg-muted/20"><div class="p-2 text-[10px] bg-muted/50 font-bold uppercase tracking-wider text-muted-foreground">Медиа: ${alt || 'картинка'}</div><div class="p-2 flex justify-center"><img src="${url}" class="max-h-60 rounded object-contain" onError="this.src=''"/></div></div>`
      )
      .replace(/\n/g, '<br>')
  } catch (e) {
    console.error('MD Render error:', e)
    return String(text)
  }
}

interface RichEditorProps {
  value: string | null | undefined
  onChange: (val: string) => void
  rows?: number
  placeholder?: string
}

export const RichEditor: FC<RichEditorProps> = ({
  value = '',
  onChange,
  rows = 16,
  placeholder,
}) => {
  const [showSheet, setShowSheet] = useState(false)
  const [showMediaSheet, setShowMediaSheet] = useState(false)
  const [viewMode, setViewMode] = useState<'edit' | 'split' | 'preview'>('edit')
  const [liveHtml, setLiveHtml] = useState('')
  const [uploading, setUploading] = useState(false)
  const [rendering, setRendering] = useState(false)
  const taRef = useRef<HTMLTextAreaElement>(null)
  const renderTimer = useRef<NodeJS.Timeout | null>(null)

  const wordCount = useMemo(() => (value || '').trim().split(/\s+/).filter(Boolean).length, [value])

  useEffect(() => {
    if (viewMode === 'edit') return
    if (renderTimer.current) clearTimeout(renderTimer.current)
    if (!value || !value.trim()) {
      setLiveHtml('')
      return
    }

    setRendering(true)
    renderTimer.current = setTimeout(async () => {
      try {
        const initData = window.Telegram?.WebApp?.initData ?? ''
        const res = await fetch((import.meta.env.VITE_API_URL ?? '') + '/api/guide/__preview__', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Telegram-Init-Data': initData,
          },
          body: JSON.stringify({ text: value }),
        })
        if (res.ok) {
          const data = await res.json()
          setLiveHtml(data.html || '')
        } else {
          setLiveHtml(renderMd(value || ''))
        }
      } catch {
        setLiveHtml(renderMd(value || ''))
      } finally {
        setRendering(false)
      }
    }, 300)

    return () => {
      if (renderTimer.current) clearTimeout(renderTimer.current)
    }
  }, [viewMode, value])

  const insertIcon = useCallback(
    (key: string) => {
      const tag = `{{${key}}}`
      const el = taRef.current
      if (!el) {
        onChange((value || '') + tag)
        setShowSheet(false)
        return
      }
      const s = el.selectionStart
      const e = el.selectionEnd
      const v = value || ''
      const next = v.slice(0, s) + tag + v.slice(e)
      onChange(next)
      requestAnimationFrame(() => {
        el.focus()
        el.setSelectionRange(s + tag.length, s + tag.length)
      })
      setShowSheet(false)
    },
    [value, onChange]
  )

  const insertMedia = useCallback(
    (url: string, type: 'image' | 'video') => {
      const tag = type === 'image' ? `\n![image](${url})\n` : `\n![video](${url})\n`
      const el = taRef.current
      if (!el) {
        onChange((value || '') + tag)
        setShowMediaSheet(false)
        return
      }
      const s = el.selectionStart
      const e = el.selectionEnd
      const v = value || ''
      const next = v.slice(0, s) + tag + v.slice(e)
      onChange(next)
      requestAnimationFrame(() => {
        el.focus()
        el.setSelectionRange(s + tag.length, s + tag.length)
      })
      setShowMediaSheet(false)
    },
    [value, onChange]
  )

  const handleDrop = async (e: React.DragEvent<HTMLTextAreaElement>) => {
    const files = e.dataTransfer?.files
    if (!files || !files.length) return
    const file = files[0]
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) return
    e.preventDefault()
    setUploading(true)
    try {
      const res = await apiUpload(file, 'guides')
      insertMedia((res as { url: string }).url, file.type.startsWith('video/') ? 'video' : 'image')
      haptic.success?.()
    } catch (err) {
      alert('Ошибка загрузки: ' + (err as Error).message)
    } finally {
      setUploading(false)
    }
  }

  const handlePaste = async (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    const items = e.clipboardData?.items
    if (!items) return
    for (const item of Array.from(items)) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile()
        if (file) {
          e.preventDefault()
          setUploading(true)
          try {
            const res = await apiUpload(file, 'guides')
            insertMedia((res as { url: string }).url, 'image')
            haptic.success?.()
          } catch (err) {
            alert('Ошибка загрузки из буфера: ' + (err as Error).message)
          } finally {
            setUploading(false)
          }
          break
        }
      }
    }
  }

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      const raw = e.target.value
      const norm = normalizeIcons(raw)
      if (norm !== raw) {
        const pos = e.target.selectionStart + (norm.length - raw.length)
        onChange(norm)
        requestAnimationFrame(() => taRef.current?.setSelectionRange(pos, pos))
      } else {
        onChange(raw)
      }
    },
    [onChange]
  )

  return (
    <div className="flex flex-col border border-border/50 rounded-[24px] overflow-hidden bg-background shadow-sm ring-1 ring-border/5">
      {/* Editor Toolbar */}
      <RichEditorToolbar textareaRef={taRef} value={value || ''} onChange={onChange} />

      {/* Action Bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-muted/20 border-b border-border/30">
        <div className="flex p-1 bg-muted/50 rounded-xl">
          <button
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95',
              viewMode === 'edit'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            )}
            type="button"
            onClick={() => setViewMode('edit')}
          >
            <Edit3 className="size-3.5" />
            Текст
          </button>
          <button
            className={cn(
              'hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95',
              viewMode === 'split'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            )}
            type="button"
            onClick={() => setViewMode('split')}
          >
            <Columns className="size-3.5" />
            Сплит
          </button>
          <button
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95',
              viewMode === 'preview'
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            )}
            type="button"
            onClick={() => setViewMode('preview')}
          >
            <Eye className="size-3.5" />
            Превью
          </button>
        </div>

        <div className="flex items-center gap-3">
          {uploading && (
            <span className="text-[10px] font-bold text-primary animate-pulse flex items-center gap-1">
              <div className="adm2-spinner adm2-spinner-sm" /> Загрузка...
            </span>
          )}
          <Button
            variant="ghost"
            size="sm"
            className="h-8 rounded-lg text-[11px] font-black uppercase text-primary hover:bg-primary/10 transition-all active:scale-95"
            onClick={() => setShowSheet(true)}
          >
            <Sparkles className="mr-1.5 size-3.5" />
            Иконки
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 rounded-lg text-[11px] font-black uppercase text-primary hover:bg-primary/10 transition-all active:scale-95"
            onClick={() => setShowMediaSheet(true)}
          >
            <ImageIcon className="mr-1.5 size-3.5" />
            Медиа
          </Button>
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-muted/60 rounded-full">
            <span className="text-[10px] font-black tracking-widest text-muted-foreground/80 uppercase">
              {wordCount} шт
            </span>
          </div>
        </div>
      </div>

      {/* Main Area */}
      <div className="relative bg-card/10">
        {viewMode === 'split' ? (
          <div className="grid grid-cols-2 divide-x divide-border/20 min-h-[350px]">
            <textarea
              ref={taRef}
              className="w-full min-h-[350px] bg-transparent p-5 text-sm font-medium leading-relaxed placeholder:text-muted-foreground/30 focus:outline-none scroll-smooth"
              rows={rows}
              value={value || ''}
              onChange={handleChange}
              onDrop={handleDrop}
              onPaste={handlePaste}
              placeholder="Перетащите сюда картинку или вставьте из буфера (Ctrl+V)..."
              spellCheck={false}
            />
            <div className="min-h-[350px] p-5 overflow-y-auto no-scrollbar">
              <div
                className="guide-content max-w-none prose prose-sm dark:prose-invert"
                // biome-ignore lint/security/noDangerouslySetInnerHtml: Split preview
                dangerouslySetInnerHTML={{
                  __html:
                    liveHtml ||
                    '<span className="text-muted-foreground italic opacity-50">Предварительный просмотр...</span>',
                }}
              />
            </div>
          </div>
        ) : viewMode === 'preview' ? (
          <div className="min-h-[300px] p-6 animate-in fade-in duration-300">
            {rendering ? (
              <div className="flex h-40 items-center justify-center">
                <div className="adm2-spinner" />
              </div>
            ) : (
              <div
                className="guide-content max-w-none prose prose-sm dark:prose-invert"
                // biome-ignore lint/security/noDangerouslySetInnerHtml: Preview rendering
                dangerouslySetInnerHTML={{
                  __html:
                    liveHtml ||
                    '<span className="text-muted-foreground italic opacity-50">Предварительный просмотр пуст...</span>',
                }}
              />
            )}
          </div>
        ) : (
          <textarea
            ref={taRef}
            className="w-full min-h-[300px] bg-transparent p-5 text-sm font-medium leading-relaxed placeholder:text-muted-foreground/30 focus:outline-none scroll-smooth"
            rows={rows}
            value={value || ''}
            onChange={handleChange}
            onDrop={handleDrop}
            onPaste={handlePaste}
            placeholder={
              placeholder ||
              'Напишите текст гайда. Можно перетащить картинку или вставить из буфера (Ctrl+V)...'
            }
            spellCheck={false}
          />
        )}
      </div>

      {/* Editor Footer Help */}
      <div className="px-4 py-3 bg-muted/10 border-t border-border/20">
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-2 gap-x-4">
          {[
            { tag: '**bold**', label: 'жирный' },
            { tag: '*italic*', label: 'курсив' },
            { tag: '~~strike~~', label: 'зачёрк.' },
            { tag: '||spoiler||', label: 'спойлер' },
            { tag: '`code`', label: 'код' },
            { tag: '> quote', label: 'цитата' },
            { tag: '- item', label: 'список' },
            { tag: '[[key|txt]]', label: 'ссылка' },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <code className="text-[10px] font-mono bg-muted/50 px-1 py-0.5 rounded text-primary/70">
                {item.tag}
              </code>
              <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground/50">
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {showSheet && <IconSheet onInsert={insertIcon} onClose={handleCloseSheet} />}
      {showMediaSheet && <MediaSheet onInsert={insertMedia} onClose={handleCloseMedia} />}
    </div>
  )
}
