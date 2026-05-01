import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { haptic } from '@/lib/haptic'
import { Hash, Plus, X } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useState } from 'react'

interface TagBadgeProps {
  tag: string
  onClick?: (tag: string) => void
  onRemove?: (tag: string) => void
  active?: boolean
  className?: string
}

/**
 * TagBadge refactored with TSX and shadcn/ui.
 * Support for active states, removal, and custom styling.
 */
export const TagBadge: React.FC<TagBadgeProps> = ({
  tag,
  onClick,
  onRemove,
  active,
  className,
}) => {
  return (
    <Badge
      variant={active ? 'default' : 'secondary'}
      className={cn(
        'cursor-pointer gap-1.5 rounded-lg border-border/30 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider transition-all active:scale-95',
        !active && 'bg-muted/50 hover:bg-muted text-muted-foreground',
        active && 'bg-primary text-primary-foreground shadow-sm shadow-primary/20',
        className
      )}
      onClick={
        onClick
          ? () => {
              haptic.light?.()
              onClick(tag)
            }
          : undefined
      }
    >
      <Hash className={cn('size-2.5 opacity-60', active && 'opacity-100')} />
      {tag}
      {onRemove && (
        <button
          className="ml-1 rounded-full p-0.5 hover:bg-white/20 transition-colors"
          onClick={(e) => {
            e.stopPropagation()
            onRemove(tag)
          }}
        >
          <X className="size-3" />
        </button>
      )}
    </Badge>
  )
}

interface TagsListProps {
  tags: string[]
  onTagClick?: (tag: string) => void
  className?: string
}

export const TagsList: React.FC<TagsListProps> = ({ tags, onTagClick, className }) => {
  if (!Array.isArray(tags) || tags.length === 0) return null
  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {tags.map((tag) => (
        <TagBadge key={tag} tag={tag} onClick={onTagClick} />
      ))}
    </div>
  )
}

interface TagEditorProps {
  tags: string[]
  onChange: (tags: string[]) => void
}

export const TagEditor: React.FC<TagEditorProps> = ({ tags, onChange }) => {
  const [input, setInput] = useState('')

  const add = (raw: string) => {
    const t = raw
      .trim()
      .toLowerCase()
      .replace(/\s+/g, '-')
      .replace(/[^a-zа-яё0-9_-]/gi, '')
    if (!t || tags.includes(t) || tags.length >= 20) return
    onChange([...tags, t])
    setInput('')
  }

  const remove = (tag: string) => onChange(tags.filter((t) => t !== tag))

  return (
    <div className="flex flex-col gap-4 py-2">
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <TagBadge key={tag} tag={tag} onRemove={remove} active />
        ))}
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1 group/field">
          <Hash className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within/field:text-primary" />
          <Input
            className="h-11 border-none bg-muted/50 pl-9 text-sm focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-primary/20"
            placeholder="Добавить тег..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault()
                add(input)
              }
            }}
            maxLength={30}
          />
        </div>
        <Button
          size="icon"
          className="h-11 w-11 shrink-0 rounded-xl"
          type="button"
          onClick={() => add(input)}
          disabled={!input.trim()}
        >
          <Plus className="size-5" />
        </Button>
      </div>

      <p className="px-1 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/40">
        Enter или запятая · макс. 20 тегов
      </p>
    </div>
  )
}
