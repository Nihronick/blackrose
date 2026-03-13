import { useState, useEffect, useRef } from 'react'
import { apiIconsGrouped } from '../api'
import { haptic } from '../haptic'

/**
 * IconLibrary — справочник всех иконок с группировкой.
 * Клик по иконке копирует {{key}} в буфер обмена.
 */
export function IconLibrary() {
  const [groups, setGroups]       = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)
  const [filter, setFilter]       = useState('')
  const [copied, setCopied]       = useState(null)  // key последней скопированной
  const [openGroups, setOpenGroups] = useState({})  // { groupId: bool }
  const toastTimer = useRef(null)

  useEffect(() => {
    apiIconsGrouped()
      .then(data => {
        setGroups(data)
        // По умолчанию открыть первые две группы
        const initial = {}
        data.slice(0, 2).forEach(g => { initial[g.id] = true })
        setOpenGroups(initial)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const handleCopy = (key) => {
    const tag = `{{${key}}}`
    navigator.clipboard?.writeText(tag).catch(() => {
      // fallback для среды без clipboard API
      const el = document.createElement('textarea')
      el.value = tag
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    })
    haptic.success?.()
    setCopied(key)
    clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setCopied(null), 1800)
  }

  const toggleGroup = (id) => {
    setOpenGroups(prev => ({ ...prev, [id]: !prev[id] }))
  }

  const expandAll  = () => {
    const all = {}
    groups.forEach(g => { all[g.id] = true })
    setOpenGroups(all)
  }
  const collapseAll = () => setOpenGroups({})

  // Фильтрация
  const q = filter.trim().toLowerCase()
  const filtered = q
    ? groups
        .map(g => ({ ...g, icons: g.icons.filter(i => i.key.toLowerCase().includes(q)) }))
        .filter(g => g.icons.length > 0)
    : groups

  const totalVisible = filtered.reduce((s, g) => s + g.icons.length, 0)

  if (loading) return <div className="admin-loading">⏳ Загрузка иконок...</div>
  if (error)   return <div className="admin-error">⚠️ {error}</div>

  return (
    <div className="icon-library">

      {/* Поиск */}
      <div className="icon-lib-search">
        <div className="search-box">
          <span className="search-icon">
            <svg viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor" fill="none" width="15" height="15">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
          </span>
          <input
            className="search-input"
            placeholder="Поиск по ключу..."
            value={filter}
            onChange={e => setFilter(e.target.value)}
            autoComplete="off"
          />
          {filter && (
            <button className="search-clear" onClick={() => setFilter('')}>✕</button>
          )}
        </div>
        <div className="icon-lib-meta">
          <span>{totalVisible} иконок</span>
          {!q && (
            <>
              <button className="icon-lib-toggle-btn" onClick={expandAll}>развернуть все</button>
              <button className="icon-lib-toggle-btn" onClick={collapseAll}>свернуть все</button>
            </>
          )}
        </div>
      </div>

      {/* Подсказка */}
      <div className="icon-lib-hint">
        👆 Нажми на иконку — скопируется <code>{'{{key}}'}</code> для вставки в текст гайда
      </div>

      {/* Группы */}
      {filtered.map(group => (
        <div key={group.id} className="icon-lib-group">
          <button
            className="icon-lib-group-header"
            onClick={() => toggleGroup(group.id)}
          >
            <span>{group.label}</span>
            <span className="icon-lib-group-count">{group.icons.length}</span>
            <span className="icon-lib-group-arrow">
              {(q || openGroups[group.id]) ? '▾' : '▸'}
            </span>
          </button>

          {(q || openGroups[group.id]) && (
            <div className="icon-lib-grid">
              {group.icons.map(icon => (
                <button
                  key={icon.key}
                  className={`icon-lib-item ${copied === icon.key ? 'icon-lib-item--copied' : ''}`}
                  onClick={() => handleCopy(icon.key)}
                  title={`Скопировать {{${icon.key}}}`}
                >
                  <img
                    src={icon.url}
                    alt={icon.key}
                    width={32}
                    height={32}
                    loading="lazy"
                    onError={e => { e.target.style.opacity = '0.2' }}
                  />
                  <span className="icon-lib-key">
                    {copied === icon.key ? '✓ скопировано' : icon.key}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      ))}

      {filtered.length === 0 && (
        <div className="state-empty">Ничего не найдено по «{filter}»</div>
      )}

      {/* Toast */}
      {copied && (
        <div className="icon-lib-toast">
          ✅ Скопировано: <code>{`{{${copied}}}`}</code>
        </div>
      )}
    </div>
  )
}
