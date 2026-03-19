/**
 * Simple drag-and-drop reorder list.
 * Works via HTML5 drag API — no external dependencies.
 * Props:
 *   items: [{key, title, icon_url}]
 *   onReorder: (newItems) => void  — called after drop
 */
import { useState, useRef } from 'react'
import { haptic } from '../haptic'

export function ReorderList({ items, onReorder, renderItem }) {
  const [list, setList]     = useState(items)
  const [dragIdx, setDragIdx] = useState(null)
  const [overIdx, setOverIdx] = useState(null)
  const dragNode = useRef(null)

  // Sync when props change
  if (items !== list && dragIdx === null) setList(items)

  const onDragStart = (e, idx) => {
    setDragIdx(idx)
    dragNode.current = e.currentTarget
    e.dataTransfer.effectAllowed = 'move'
    haptic.light()
  }

  const onDragOver = (e, idx) => {
    e.preventDefault()
    if (idx === dragIdx) return
    setOverIdx(idx)
  }

  const onDrop = (e, idx) => {
    e.preventDefault()
    if (dragIdx === null || dragIdx === idx) return
    const next = [...list]
    const [moved] = next.splice(dragIdx, 1)
    next.splice(idx, 0, moved)
    setList(next)
    setDragIdx(null)
    setOverIdx(null)
    haptic.medium()
    onReorder(next)
  }

  const onDragEnd = () => { setDragIdx(null); setOverIdx(null) }

  return (
    <div style={{display:'flex', flexDirection:'column', gap:'6px'}}>
      {list.map((item, idx) => (
        <div
          key={item.key}
          draggable
          onDragStart={e => onDragStart(e, idx)}
          onDragOver={e => onDragOver(e, idx)}
          onDrop={e => onDrop(e, idx)}
          onDragEnd={onDragEnd}
          style={{
            opacity: dragIdx === idx ? 0.4 : 1,
            outline: overIdx === idx ? '2px solid var(--accent)' : 'none',
            borderRadius: 'var(--radius)',
            cursor: 'grab',
            transition: 'opacity .15s',
          }}
        >
          {renderItem(item, idx)}
        </div>
      ))}
    </div>
  )
}
