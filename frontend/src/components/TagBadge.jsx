import { useState } from 'react'
import { haptic } from '../haptic'

export function TagBadge({ tag, onClick, onRemove, active }) {
  return (
    <span
      className={`tag-badge${active ? ' active' : ''}${onClick ? ' clickable' : ''}`}
      onClick={onClick ? () => { haptic.light(); onClick(tag) } : undefined}
    >
      #{tag}
      {onRemove && (
        <button className="tag-remove" onClick={e => { e.stopPropagation(); onRemove(tag) }}>×</button>
      )}
    </span>
  )
}

export function TagsList({ tags, onTagClick }) {
  if (!tags || tags.length === 0) return null
  return (
    <div className="tags-row">
      {tags.map(tag => (
        <TagBadge key={tag} tag={tag} onClick={onTagClick} />
      ))}
    </div>
  )
}

export function TagEditor({ tags, onChange }) {
  const [input, setInput] = useState('')

  const add = (raw) => {
    const t = raw.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-zа-яё0-9_-]/gi, '')
    if (!t || tags.includes(t) || tags.length >= 20) return
    onChange([...tags, t])
    setInput('')
  }

  const remove = (tag) => onChange(tags.filter(t => t !== tag))

  return (
    <div className="tag-editor">
      <div className="tags-row" style={{ flexWrap: 'wrap', gap: '6px', marginBottom: tags.length ? '8px' : 0 }}>
        {tags.map(tag => (
          <TagBadge key={tag} tag={tag} onRemove={remove} />
        ))}
      </div>
      <div className="tag-input-row">
        <input
          className="adm2-input"
          placeholder="Добавить тег..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add(input) }
          }}
          maxLength={30}
        />
        <button className="adm2-btn-sm" type="button" onClick={() => add(input)} disabled={!input.trim()}>+</button>
      </div>
      <div className="tag-hint">Enter или запятая · макс. 20 тегов</div>
    </div>
  )
}
