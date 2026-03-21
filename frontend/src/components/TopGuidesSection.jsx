import { useState, useEffect } from 'react'
import { apiTopGuides } from '../api'
import { haptic } from '../haptic'

const EYE_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" width="10" height="10">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
)

function formatViews(n) {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

export function TopGuidesSection({ onSelectGuide }) {
  const [guides, setGuides] = useState(null)
  const [open, setOpen]     = useState(false)

  useEffect(() => {
    if (!open) return
    apiTopGuides()
      .then(res => setGuides(res.results || []))
      .catch(() => setGuides([]))
  }, [open])

  if (!open) {
    return (
      <div style={{ padding: '0 16px 8px' }}>
        <button className="fav-bar-btn" onClick={() => { haptic.light(); setOpen(true) }}>
          {EYE_ICON}
          <span>Популярное</span>
        </button>
      </div>
    )
  }

  return (
    <div style={{ padding: '0 16px 12px' }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 8,
      }}>
        <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)' }}>
          Топ просматриваемых
        </span>
        <button
          onClick={() => { haptic.light(); setOpen(false) }}
          style={{
            background: 'none', border: 'none', padding: '2px 6px',
            color: 'var(--text-secondary)', cursor: 'pointer', fontSize: 13,
          }}
        >
          Скрыть
        </button>
      </div>

      {!guides && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton-card">
              <div className="sk-icon skeleton"/>
              <div className="sk-body">
                <div className="sk-title skeleton"/>
                <div className="sk-sub skeleton"/>
              </div>
            </div>
          ))}
        </div>
      )}

      {guides && guides.length === 0 && (
        <div className="state-empty">Нет данных</div>
      )}

      {guides && guides.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {guides.map((g, idx) => (
            <div
              key={g.key}
              className="card"
              onClick={() => { haptic.light(); onSelectGuide(g.key, g.title, g.icon_url) }}
              style={{ padding: '10px 12px' }}
            >
              <span style={{
                fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)',
                minWidth: 20, textAlign: 'center',
              }}>
                {idx + 1}
              </span>
              {g.icon_url && (
                <img src={g.icon_url} alt="" width={32} height={32}
                  style={{ borderRadius: 8, flexShrink: 0 }}
                  onError={e => e.target.style.display = 'none'}/>
              )}
              <div className="card-body">
                <div className="card-title" style={{ fontSize: 14 }}>{g.title}</div>
                {g.views > 0 && (
                  <div className="card-meta">
                    <span className="views-pill">
                      {EYE_ICON} {formatViews(g.views)}
                    </span>
                  </div>
                )}
              </div>
              <span className="card-arrow">›</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
