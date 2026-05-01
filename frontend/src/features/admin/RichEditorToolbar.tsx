import { Button } from '@/components/ui/button'
import { haptic } from '@/lib/haptic'
import {
  Bold,
  Code,
  Eye,
  Hash,
  Italic,
  LinkIcon,
  List,
  ListOrdered,
  Quote,
  Strikethrough,
  Underline,
} from '@/lib/icons'
import React, { useCallback, useMemo } from 'react'
import { IC } from './adminIcons'

interface ToolbarItem {
  icon?: string
  lucide?: React.ElementType
  html?: string
  title: string
  wrap?: [string, string]
  prefix?: string
}

interface ToolbarConfig {
  divider?: boolean
  items?: ToolbarItem[]
}

const TOOLBAR: ToolbarConfig[] = [
  {
    items: [
      { html: 'H2', title: 'Заголовок 2', wrap: ['## ', ''] },
      { html: 'H3', title: 'Заголовок 3', wrap: ['### ', ''] },
    ],
  },
  { divider: true },
  {
    items: [
      { lucide: Bold, icon: 'bold', title: 'Жирный **B**', wrap: ['**', '**'] },
      { lucide: Italic, icon: 'italic', title: 'Курсив *I*', wrap: ['*', '*'] },
      { lucide: Underline, icon: 'under', title: 'Подчёркнутый', wrap: ['<u>', '</u>'] },
      { lucide: Strikethrough, icon: 'strike', title: 'Зачёркнутый ~~S~~', wrap: ['~~', '~~'] },
    ],
  },
  { divider: true },
  {
    items: [
      { lucide: Code, icon: 'code', title: 'Код `code`', wrap: ['`', '`'] },
      { lucide: Quote, icon: 'quote', title: 'Цитата > …', wrap: ['> ', ''] },
      { lucide: LinkIcon, icon: 'link', title: 'Ссылка [text](url)', wrap: ['[', '](url)'] },
      { lucide: Eye, icon: 'spoil', title: 'Спойлер ||text||', wrap: ['||', '||'] },
    ],
  },
  { divider: true },
  {
    items: [
      { lucide: List, icon: 'ul', title: 'Маркированный список', prefix: '- ' },
      { lucide: ListOrdered, icon: 'ol', title: 'Нумерованный список', prefix: '1. ' },
    ],
  },
  { divider: true },
  {
    items: [{ lucide: Hash, icon: 'cyber', title: 'Киберссылка [[key]]', wrap: ['[[', ']]'] }],
  },
]

interface RichEditorToolbarProps {
  textareaRef: React.RefObject<HTMLTextAreaElement | null>
  value: string
  onChange: (val: string) => void
}

const RichEditorToolbar: React.FC<RichEditorToolbarProps> = ({ textareaRef, value, onChange }) => {
  const apply = useCallback(
    (item: ToolbarItem) => {
      const el = textareaRef.current
      if (!el) return

      const s = el.selectionStart
      const e = el.selectionEnd
      const sel = value.slice(s, e)
      let next: string
      let cur: number

      if (item.prefix) {
        const before = value.slice(0, s)
        const lineStart = before.lastIndexOf('\n') + 1
        const lines = value.slice(lineStart, e).split('\n')
        const rep = lines.map((l) => item.prefix! + l).join('\n')
        next = value.slice(0, lineStart) + rep + value.slice(e)
        cur = lineStart + rep.length
      } else if (item.wrap) {
        const [o, c] = item.wrap
        const ph = o.startsWith('#') ? 'Заголовок' : o === '> ' ? 'Текст цитаты' : 'текст'
        const ins = sel || ph
        next = value.slice(0, s) + o + ins + c + value.slice(e)
        cur = s + o.length + ins.length
      } else {
        return
      }

      onChange(next)
      requestAnimationFrame(() => {
        el.focus()
        el.setSelectionRange(cur, cur)
      })
      haptic.light?.()
    },
    [textareaRef, value, onChange]
  )

  const handleMouseDown = useCallback(
    (item: ToolbarItem) => (ev: React.MouseEvent) => {
      ev.preventDefault()
      apply(item)
    },
    [apply]
  )

  const toolbarGroups = useMemo(() => TOOLBAR, [])

  return (
    <div className="flex items-center flex-wrap gap-1 p-2 bg-muted/40 border-b border-border/50 no-scrollbar overflow-x-auto whitespace-nowrap">
      {toolbarGroups.map((group, i) => {
        if (group.divider)
          return <div key={`div-${i}`} className="w-[1px] h-4 bg-border/40 mx-1 shrink-0" />
        return (
          <div key={`group-${i}`} className="flex items-center gap-0.5">
            {group.items?.map((btn, j) => (
              <Button
                key={j}
                type="button"
                variant="ghost"
                size="icon"
                className="size-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/80 transition-all hover:scale-105 active:scale-95 shrink-0"
                title={btn.title}
                onMouseDown={handleMouseDown(btn)}
              >
                {btn.lucide ? (
                  <btn.lucide className="size-4" />
                ) : btn.icon ? (
                  IC[btn.icon as keyof typeof IC]
                ) : (
                  <span className="text-[10px] font-bold">{btn.html}</span>
                )}
              </Button>
            ))}
          </div>
        )
      })}
    </div>
  )
}

export default React.memo(RichEditorToolbar)
