import { useState, useEffect, useRef, useCallback } from 'react'
import { apiFetch } from '../api'
import { haptic } from '../haptic'
import { SkeletonList } from '../components/Skeleton'
import { CardIcon } from '../components/CardIcon'
import { ContentBadges } from '../components/ContentBadges'
import { TagBadge } from '../components/TagBadge'
import { PtrIndicator } from '../components/PtrIndicator'
import { usePullToRefresh } from '../hooks/usePullToRefresh'

const BELL_ON = (
  <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0"/>
  </svg>
)
const BELL_OFF = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="18" height="18">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0"/>
  </svg>
)

export function GuidesView({ category, onSelectGuide, isSubscribed, onToggleSubscription }) {
  const [items, setItems] = useState(null)
  const [error, setError] = useState(null)
  const scrollRef = useRef(null)

  const load = useCallback(async () => {
    try {
      const res = await apiFetch(`/api/category/${category.key}`)
      setItems(res.items); setError(null)
    } catch (e) {
      if (e.message !== 'ACCESS_DENIED') setError(e.message)
    }
  }, [category.key])

  useEffect(() => { load() }, [load])

  const { pullY, refreshing } = usePullToRefresh(scrollRef, load)
  const subscribed = isSubscribed?.(category.key)

  return (
    <div className="view-scroll" ref={scrollRef}>
      <PtrIndicator pullY={pullY} refreshing={refreshing} />

      {/* Subscription button */}
      {onToggleSubscription && (
        <div className="guides-sub-bar">
          <button
            className={`sub-btn${subscribed ? ' active' : ''}`}
            onClick={() => { haptic.light(); onToggleSubscription(category.key) }}
          >
            {subscribed ? BELL_ON : BELL_OFF}
            <span>{subscribed ? 'Подписан' : 'Подписаться на обновления'}</span>
          </button>
        </div>
      )}

      {error && <div className="list"><div className="state-error">{error}</div></div>}
      {!error && !items && <SkeletonList count={6} />}
      {!error && items && (
        <div className="list">
          {items.length === 0
            ? <div className="state-empty">Нет гайдов в этом разделе</div>
            : items.map(item => (
                <div key={item.key} className="card"
                  onClick={() => { haptic.light(); onSelectGuide(item.key) }}>
                  <CardIcon url={item.icon} placeholder="📖" />
                  <div className="card-body">
                    <div className="card-title">{item.title}</div>
                    <div className="card-meta">
                      <ContentBadges hasPhoto={item.has_photo} hasVideo={item.has_video} hasDocument={item.has_document} />
                      {item.views > 0 && (
                        <span className="views-pill">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="10" height="10">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                          </svg>
                          {item.views >= 1000 ? `${(item.views/1000).toFixed(1)}k` : item.views}
                        </span>
                      )}
                    </div>
                    {item.preview && <div className="card-subtitle">{item.preview}</div>}
                    {item.tags?.length > 0 && (
                      <div className="card-tags">
                        {item.tags.slice(0, 3).map(t => <TagBadge key={t} tag={t} />)}
                      </div>
                    )}
                  </div>
                  <span className="card-arrow">›</span>
                </div>
              ))
          }
        </div>
      )}
    </div>
  )
}
