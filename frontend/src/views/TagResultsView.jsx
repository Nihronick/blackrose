import { useState, useEffect } from 'react'
import { apiGuidesByTag } from '../api'
import { haptic } from '../haptic'

export function TagResultsView({ tag, onSelectGuide }) {
  const [items, setItems] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiGuidesByTag(tag)
      .then(res => setItems(res.results || []))
      .catch(e => { if (e.message !== 'ACCESS_DENIED') setError(e.message) })
  }, [tag])

  if (error) return (
    <div className="list">
      <div className="state-error">{error}</div>
    </div>
  )

  if (!items) return (
    <div className="list">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="skeleton-card">
          <div className="sk-icon skeleton"/>
          <div className="sk-body">
            <div className="sk-title skeleton"/>
            <div className="sk-sub skeleton"/>
          </div>
        </div>
      ))}
    </div>
  )

  return (
    <div className="view-scroll">
      <div className="list">
        {items.length === 0
          ? <div className="state-empty">Гайдов с тегом #{tag} не найдено</div>
          : items.map(item => (
              <div key={item.key} className="card"
                onClick={() => { haptic.light(); onSelectGuide(item.key) }}>
                {item.icon_url && (
                  <img src={item.icon_url} alt="" width={44} height={44}
                    style={{ borderRadius: 10, flexShrink: 0 }}
                    onError={e => e.target.style.display = 'none'}/>
                )}
                <div className="card-body">
                  <div className="card-title">{item.title}</div>
                  <div className="card-meta">
                    <span className="card-subtitle">📂 {item.category_key}</span>
                  </div>
                </div>
                <span className="card-arrow">›</span>
              </div>
            ))
        }
      </div>
    </div>
  )
}
