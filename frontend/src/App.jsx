import { useState, useEffect, useCallback } from 'react'
import { apiFetch } from './api'
import { haptic } from './haptic'
import { tgApp } from './theme'
import { useFavorites } from './hooks/useFavorites'
import { FabButton } from './components/FabButton'
import { QuickNav } from './components/QuickNav'
import { AccessDeniedView } from './views/AccessDeniedView'
import { CategoriesView } from './views/CategoriesView'
import { GuidesView } from './views/GuidesView'
import { GuideView } from './views/GuideView'
import { FavoritesView } from './views/FavoritesView'

const BACK_ICON = (
  <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
    <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
  </svg>
)

const STAR_ICON = (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
)

export function App() {
  const [view, setView]         = useState('categories')
  const [accessMsg, setAccessMsg] = useState(null)
  const [category, setCategory] = useState(null)
  const [guideKey, setGuideKey] = useState(null)
  const [cats, setCats]         = useState([])
  const [showQN, setShowQN]     = useState(false)

  const { favorites, loaded: favsLoaded, toggle: toggleFav, isFavorite } = useFavorites()

  // Auth
  useEffect(() => {
    const tg = window.Telegram?.WebApp
    const doAuth = () => {
      apiFetch('/api/auth').catch(e => {
        if (e.message === 'ACCESS_DENIED') { setAccessMsg(e.detail); setView('access_denied') }
      })
    }
    if (tg?.initData) { doAuth() } else { setTimeout(doAuth, 500) }
  }, [])

  // Back navigation
  const goBack = useCallback(() => {
    haptic.light()
    if (view === 'guide')      { setView('guides');      return }
    if (view === 'guides')     { setView('categories');  return }
    if (view === 'favorites')  { setView('categories');  return }
  }, [view])

  useEffect(() => {
    const noBack = view === 'categories' || view === 'access_denied'
    noBack ? tgApp?.BackButton?.hide() : tgApp?.BackButton?.show()
    if (!noBack) history.pushState({ view }, '')

    tgApp?.BackButton?.onClick(goBack)
    const onPop = e => { e.preventDefault(); goBack() }
    window.addEventListener('popstate', onPop)
    return () => {
      tgApp?.BackButton?.offClick(goBack)
      window.removeEventListener('popstate', onPop)
    }
  }, [view, goBack])

  const openCategory = cat => { setCategory(cat); setView('guides') }
  const openGuide    = key => { setGuideKey(key); setView('guide')  }

  const fabVisible = view === 'guides' || view === 'guide'
  const fabLabel   = view === 'guide' ? 'Назад' : 'Категории'

  return (
    <div className="app-shell">

      {/* Header */}
      {(view === 'guides' || view === 'guide' || view === 'favorites') && (
        <div className="header">
          <div className="header-top">
            <button className="header-back" onClick={goBack}>{BACK_ICON}</button>
            <div className="header-titles">
              <div className="header-title">
                {view === 'favorites' && 'Избранное'}
                {view === 'guides' && category?.title}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Кнопка избранного на главном экране */}
      {view === 'categories' && favsLoaded && favorites.length > 0 && (
        <div className="fav-bar">
          <button className="fav-bar-btn" onClick={() => { haptic.light(); setView('favorites') }}>
            {STAR_ICON}
            <span>Избранное</span>
            <span className="fav-bar-count">{favorites.length}</span>
          </button>
        </div>
      )}

      {/* Views */}
      {view === 'access_denied' && <AccessDeniedView message={accessMsg} />}
      {view === 'categories' && (
        <CategoriesView
          onSelectCategory={openCategory}
          onSelectGuide={openGuide}
          onCategoriesLoaded={setCats}
        />
      )}
      {view === 'guides' && category && (
        <GuidesView category={category} onSelectGuide={openGuide} />
      )}
      {view === 'guide' && guideKey && (
        <GuideView
          guideKey={guideKey}
          isFavorite={isFavorite(guideKey)}
          onToggleFavorite={toggleFav}
        />
      )}
      {view === 'favorites' && (
        <FavoritesView
          favorites={favorites}
          onSelectGuide={openGuide}
          onToggle={toggleFav}
        />
      )}

      {/* FAB */}
      <FabButton visible={fabVisible} label={fabLabel} onBack={goBack} onHoldComplete={() => setShowQN(true)} />

      {/* Quick Nav */}
      {showQN && (
        <QuickNav
          categories={cats}
          onSelect={cat  => { setShowQN(false); openCategory(cat) }}
          onHome={()     => { setShowQN(false); setView('categories') }}
          onClose={()    => setShowQN(false)}
        />
      )}
    </div>
  )
}
