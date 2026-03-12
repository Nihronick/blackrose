import { useState, useEffect, useRef, useCallback } from 'react'
import { apiFetch } from '../api'
import { haptic } from '../haptic'
import { pluralize } from '../utils'
import { SkeletonList } from '../components/Skeleton'
import { CardIcon } from '../components/CardIcon'
import { PtrIndicator } from '../components/PtrIndicator'
import { usePullToRefresh } from '../hooks/usePullToRefresh'

export function CategoriesView({ onSelectCategory, onSelectGuide, onCategoriesLoaded }) {
  const [categories, setCategories] = useState(null)
  const [error, setError]           = useState(null)
  const [search, setSearch]         = useState('')
  const [searchResults, setResults] = useState(null)
  const scrollRef  = useRef(null)
  const searchTimer = useRef(null)

  const loadCategories = useCallback(async () => {
    try {
      const res = await apiFetch('/api/categories')
      setCategories(res.categories)
      setError(null)
      onCategoriesLoaded?.(res.categories)
    } catch (e) {
      if (e.message !== 'ACCESS_DENIED') setError(e.message)
    }
  }, [onCategoriesLoaded])

  useEffect(() => { loadCategories() }, [loadCategories])

  useEffect(() => {
    clearTimeout(searchTimer.current)
    if (search.trim().length < 2) { setResults(null); return }
    searchTimer.current = setTimeout(async () => {
      try {
        const res = await apiFetch(`/api/search?q=${encodeURIComponent(search.trim())}`)
        setResults(res.results)
      } catch {}
    }, 300)
    return () => clearTimeout(searchTimer.current)
  }, [search])

  const { pullY, refreshing } = usePullToRefresh(scrollRef, loadCategories, !search)
  const isSearch = searchResults !== null
  const list     = isSearch ? searchResults : categories

  return (
    <div className="view-scroll" ref={scrollRef}>
      <div className="header">
        <div className="header-top">
          <div className="header-titles">
            <div className="header-title">BlackRose Guides</div>
            <div className="header-subtitle">Справочник гильдии</div>
          </div>
        </div>
        <div className="search-wrap">
          <div className="search-box">
            <span className="search-icon">
              <svg viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor" fill="none" width="16" height="16">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
            </span>
            <input className="search-input" type="search" placeholder="Поиск гайда..."
              value={search} onChange={e => setSearch(e.target.value)} autoComplete="off" />
            {search && <button className="search-clear" onClick={() => setSearch('')}>✕</button>}
          </div>
        </div>
      </div>

      <PtrIndicator pullY={pullY} refreshing={refreshing} />

      {error && <div className="list"><div className="state-error">{error}</div></div>}
      {!error && !list && <SkeletonList count={7} />}
      {!error && list && (
        <div className="list">
          {list.length === 0
            ? <div className="state-empty">Ничего не найдено</div>
            : list.map(item => (
                <div key={item.key} className="card"
                  onClick={() => { haptic.light(); isSearch ? onSelectGuide(item.key) : onSelectCategory(item) }}>
                  <CardIcon url={item.icon} placeholder="📁" />
                  <div className="card-body">
                    <div className="card-title">{item.title}</div>
                    <div className="card-meta">
                      {!isSearch && item.count !== undefined && (
                        <span className="count-pill">{item.count} {pluralize(item.count,'гайд','гайда','гайдов')}</span>
                      )}
                      {isSearch && item.preview && <span className="card-subtitle">{item.preview}</span>}
                    </div>
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
