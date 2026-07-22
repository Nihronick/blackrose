import { ChevronDown, ChevronUp, List } from '@/lib/icons'
import { type FC, useMemo, useState } from 'react'

interface TocItem {
  id: string
  text: string
  level: number
}

interface TableOfContentsProps {
  text: string
}

export function extractHeadings(markdownText: string): TocItem[] {
  if (!markdownText) return []
  const lines = markdownText.split('\n')
  const items: TocItem[] = []
  let index = 0

  for (const line of lines) {
    const match = line.match(/^(##|###)\s+(.+)$/)
    if (match) {
      const level = match[1].length === 2 ? 2 : 3
      const text = match[2]
        .trim()
        .replace(/\*\*/g, '')
        .replace(/\{\{\w+\}\}/g, '')
      const id = `heading-${index++}-${text.toLowerCase().replace(/[^\wа-яe]+/gi, '-')}`
      items.push({ id, text, level })
    }
  }

  return items
}

export const TableOfContents: FC<TableOfContentsProps> = ({ text }) => {
  const [collapsed, setCollapsed] = useState(false)
  const headings = useMemo(() => extractHeadings(text), [text])

  if (headings.length < 2) return null

  const scrollToHeading = (id: string) => {
    // Search for matching header text element in DOM
    const target =
      document.getElementById(id) ||
      Array.from(document.querySelectorAll('h2, h3')).find(
        (el) =>
          el.getAttribute('data-toc-id') === id ||
          el.textContent?.includes(id.split('-').pop() || '')
      )
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  return (
    <div className="my-6 border border-border/40 rounded-3xl bg-muted/20 p-4 shadow-sm backdrop-blur-sm animate-in fade-in duration-300">
      <div
        className="flex items-center justify-between cursor-pointer select-none"
        onClick={() => setCollapsed(!collapsed)}
      >
        <div className="flex items-center gap-2">
          <List className="size-4 text-primary" />
          <span className="text-xs font-black uppercase tracking-wider text-foreground">
            Содержание ({headings.length})
          </span>
        </div>
        <button type="button" className="text-muted-foreground hover:text-foreground">
          {collapsed ? <ChevronDown className="size-4" /> : <ChevronUp className="size-4" />}
        </button>
      </div>

      {!collapsed && (
        <div className="mt-3 pt-3 border-t border-border/20 space-y-1.5 max-h-60 overflow-y-auto no-scrollbar">
          {headings.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`w-full text-left font-medium text-xs py-1 px-2.5 rounded-xl transition-colors hover:bg-primary/10 hover:text-primary truncate block ${
                item.level === 3 ? 'pl-6 text-muted-foreground/80' : 'text-foreground font-bold'
              }`}
              onClick={() => scrollToHeading(item.id)}
            >
              {item.text}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
