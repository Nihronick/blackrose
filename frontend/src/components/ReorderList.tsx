import { ReactNode, DragEvent } from 'react';
import { haptic } from '@/lib/haptic'
import { GripVertical } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useEffect, useRef, useState } from 'react'

interface ReorderListProps<T> {
  items: T[]
  onReorder: (newItems: T[]) => void
  renderItem: (item: T, index: number) => ReactNode
}

export function ReorderList<T extends { key: string }>({
  items,
  onReorder,
  renderItem,
}: ReorderListProps<T>) {
  const [list, setList] = useState<T[]>(items)
  const [dragIdx, setDragIdx] = useState<number | null>(null)
  const [overIdx, setOverIdx] = useState<number | null>(null)
  const dragNode = useRef<HTMLDivElement>(null)

  // Sync when props change, but only when not dragging
  useEffect(() => {
    if (dragIdx === null) {
      setList(items)
    }
  }, [items, dragIdx])

  const handleDragStart = (e: DragEvent<HTMLDivElement>, idx: number) => {
    setDragIdx(idx)
    // @ts-ignore
    dragNode.current = e.currentTarget
    e.dataTransfer.effectAllowed = 'move'

    // Set drag image (optional, default is the element itself)
    const ghost = e.currentTarget.cloneNode(true) as HTMLElement
    ghost.style.position = 'absolute'
    ghost.style.top = '-1000px'
    document.body.appendChild(ghost)
    e.dataTransfer.setDragImage(ghost, 0, 0)
    setTimeout(() => document.body.removeChild(ghost), 0)

    haptic.light?.()
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>, idx: number) => {
    e.preventDefault()
    if (idx === dragIdx) return
    setOverIdx(idx)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>, idx: number) => {
    e.preventDefault()
    if (dragIdx === null || dragIdx === idx) return

    const next = [...list]
    const [moved] = next.splice(dragIdx, 1)
    next.splice(idx, 0, moved)

    setList(next)
    setDragIdx(null)
    setOverIdx(null)

    haptic.medium?.()
    onReorder(next)
  }

  const handleDragEnd = () => {
    setDragIdx(null)
    setOverIdx(null)
  }

  return (
    <div className="flex flex-col gap-2">
      {list.map((item, idx) => (
        <div
          key={item.key}
          draggable
          onDragStart={(e) => handleDragStart(e, idx)}
          onDragOver={(e) => handleDragOver(e, idx)}
          onDrop={(e) => handleDrop(e, idx)}
          onDragEnd={handleDragEnd}
          className={cn(
            'relative group flex items-stretch gap-2 transition-all duration-200',
            dragIdx === idx && 'opacity-40 grayscale scale-[0.98]',
            overIdx === idx &&
              'ring-2 ring-primary ring-offset-2 ring-offset-background rounded-2xl'
          )}
        >
          {/* Drag Handle */}
          <div className="flex items-center justify-center w-8 cursor-grab active:cursor-grabbing text-muted-foreground/20 group-hover:text-primary transition-colors">
            <GripVertical className="size-4" />
          </div>

          <div className="flex-1 min-w-0">{renderItem(item, idx)}</div>
        </div>
      ))}
    </div>
  )
}
