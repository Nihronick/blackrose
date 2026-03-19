import { useState, useEffect, useCallback } from 'react'
import { apiFetch } from './api'
import { haptic } from './haptic'
import { tgApp } from './theme'
import { useFavorites } from './hooks/useFavorites'
import { useHistory } from './hooks/useHistory'
import { FabButton } from './components/FabButton'
import { QuickNav } from './components/QuickNav'
import { AccessDeniedView } from './views/AccessDeniedView'
import { CategoriesView } from './views/CategoriesView'
import { GuidesView } from './views/GuidesView'
import { GuideView } from './views/GuideView'
import { FavoritesView } from './views/FavoritesView'
import { HistoryView } from './views/HistoryView'
import { AdminView } from './views/AdminView'

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
const HISTORY_ICON = (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
  </svg>
)

export function App() {
  const [view, setView]           = useState('categories')
  const [accessMsg, setAccessMsg] = useState(null)
  const [category, setCategory]   = useState(null)
  const [guideKey, setGuideKey]   = useState(null)
  const [cats, setCats]           = useState([])
  const [showQN, setShowQN]       = useState(false)
  const [isAdmin, setIsAdmin]     = useState(false)

  const { favorites, loaded: favsLoaded, toggle: toggleFav, isFavorite } = useFavorites()
  const { history, addToHistory } = useHistory()

  // Auth + deep link on load
  useEffect(() => {
    const tg = window.Telegram?.WebApp
    const doAuth = () => {
      apiFetch('/api/auth')
        .then(data => { if (data.is_admin === true) setIsAdmin(true) })
        .catch(e => {
          if (e.message === 'ACCESS_DENIED') { setAccessMsg(e.detail); setView('access_denied') }
        })
    }
    const delay = tg?.initData ? 0 : 300
    setTimeout(doAuth, delay)

    // Deep link: ?guide=key
    const params = new URLSearchParams(window.location.search)
    const deepGuide = params.get('guide')
    if (deepGuide) {
      setGuideKey(deepGuide)
      setView('guide')
    }
  }, [])

  // Back navigation
  const goBack = useCallback(() => {
    haptic.light()
    if (view === 'guide')    { setView('guides');     return }
    if (view === 'guides')   { setView('categories'); return }
    if (view === 'favorites'){ setView('categories'); return }
    if (view === 'history')  { setView('categories'); return }
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

  const openGuide = useCallback((key, title, icon) => {
    setGuideKey(key)
    setView('guide')
    // Add to history (title/icon may not be known yet — GuideView will fill them in)
    if (key) addToHistory({ key, title: title || key, icon: icon || '' })
  }, [addToHistory])

  const fabVisible = view === 'guides' || view === 'guide'
  const fabLabel   = view === 'guide' ? 'Назад' : 'Категории'

  return (
    <div className="app-shell">

      {/* Header */}
      {(view === 'guides' || view === 'guide' || view === 'favorites' || view === 'history') && (
        <div className="header">
          <div className="header-top">
            <button className="header-back" onClick={goBack}>{BACK_ICON}</button>
            <div className="header-titles">
              <div className="header-title">
                {view === 'favorites' && 'Избранное'}
                {view === 'history'   && 'История'}
                {view === 'guides'    && category?.title}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick actions on main screen */}
      {view === 'categories' && favsLoaded && (favorites.length > 0 || history.length > 0) && (
        <div className="quick-bar">
          {favorites.length > 0 && (
            <button className="fav-bar-btn" onClick={() => { haptic.light(); setView('favorites') }}>
              {STAR_ICON}
              <span>Избранное</span>
              <span className="fav-bar-count">{favorites.length}</span>
            </button>
          )}
          {history.length > 0 && (
            <button className="fav-bar-btn" onClick={() => { haptic.light(); setView('history') }}>
              {HISTORY_ICON}
              <span>Недавние</span>
              <span className="fav-bar-count">{Math.min(history.length, 9)}</span>
            </button>
          )}
        </div>
      )}

      {view === 'categories' && isAdmin && (
        <div style={{padding:'0 16px 8px'}}>
          <button className="fav-bar-btn" onClick={() => { haptic.light(); setView('admin') }}
            style={{color:'var(--text-secondary)'}}>
            ⚙️ <span>Администрирование</span>
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
          onOpenGuide={openGuide}
          onGuideLoaded={(g) => addToHistory({ key: g.key, title: g.title, icon: g.icon })}
        />
      )}
      {view === 'favorites' && (
        <FavoritesView
          favorites={favorites}
          onSelectGuide={openGuide}
          onToggle={toggleFav}
        />
      )}
      {view === 'history' && (
        <HistoryView
          history={history}
          onSelectGuide={openGuide}
        />
      )}
      {view === 'admin' && (
        <AdminView onClose={() => setView('categories')} />
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
