import { useState, useEffect, useRef, useCallback } from 'react'
import { apiFetch } from '../api'
import { haptic } from '../haptic'
import { SkeletonList } from '../components/Skeleton'
import { CardIcon } from '../components/CardIcon'
import { ContentBadges } from '../components/ContentBadges'
import { PtrIndicator } from '../components/PtrIndicator'
import { usePullToRefresh } from '../hooks/usePullToRefresh'

export function GuidesView({ category, onSelectGuide }) {
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

  return (
    <div className="view-scroll" ref={scrollRef}>
      <PtrIndicator pullY={pullY} refreshing={refreshing} />
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
                    </div>
                    {item.preview && <div className="card-subtitle">{item.preview}</div>}
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
