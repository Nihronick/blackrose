import { ErrorBoundary } from '@/components/ErrorBoundary'
import { FabButton } from '@/components/FabButton'
import { Header } from '@/components/Header'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { Category } from '@/features/categories'
import { useAppInitialization } from '@/hooks/useAppInitialization'
import { useFavorites } from '@/hooks/useFavorites'
import { useHistory } from '@/hooks/useHistory'
import { useSheet } from '@/hooks/useSheet'
import { useTelegramBackButton } from '@/hooks/useTelegramBackButton'
import { isTelegram } from '@/lib/auth'
import { haptic } from '@/lib/haptic'
import { ChevronRight, Clock, LogIn, ShieldCheck, Star } from '@/lib/icons'
import { applyLanguageKey } from '@/lib/language'
import { useAppNavigation } from '@/lib/navigation'
import { useAppStore } from '@/store'
import { AnimatePresence, motion } from 'framer-motion'
import type React from 'react'
import { Suspense, lazy, useEffect, useMemo, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useParams } from 'react-router-dom'
import { Toaster, toast } from 'sonner'

// Lazy loaded views
const CategoriesView = lazy(() => import('@/views/CategoriesView'))
const FavoritesView = lazy(() =>
  import('@/views/FavoritesView').then((m) => ({ default: m.FavoritesView }))
)
const GuideView = lazy(() => import('@/views/GuideView').then((m) => ({ default: m.GuideView })))
const GuidesView = lazy(() => import('@/views/GuidesView').then((m) => ({ default: m.GuidesView })))
const HistoryView = lazy(() =>
  import('@/views/HistoryView').then((m) => ({ default: m.HistoryView }))
)
const TagResultsView = lazy(() =>
  import('@/views/TagResultsView').then((m) => ({ default: m.TagResultsView }))
)
const AdminView = lazy(() => import('@/views/AdminView').then((m) => ({ default: m.AdminView })))
const AdminLoginModal = lazy(() =>
  import('@/components/AdminLoginModal').then((m) => ({ default: m.AdminLoginModal }))
)
const QuickNav = lazy(() => import('@/components/QuickNav').then((m) => ({ default: m.QuickNav })))

const ViewLoader = () => (
  <div className="flex h-full items-center justify-center">
    <div className="adm2-spinner" />
  </div>
)

type AppSheet = { type: 'login' } | { type: 'quickNav' }

export const App: React.FC = () => {
  const { push } = useAppNavigation()
  const location = useLocation()
  const inTelegram = isTelegram()
  const sheet = useSheet<AppSheet>()
  const [logoFailed, setLogoFailed] = useState(false)

  const { isAdmin, cats, language, setLanguage, setIsAdmin, setCats, theme, setTheme } =
    useAppStore()
  const { favorites, loaded: favsLoaded, toggle: toggleFav, isFavorite } = useFavorites()
  const { history, addToHistory } = useHistory()

  useAppInitialization()
  const { handleBack } = useTelegramBackButton()

  // Apply Theme
  useEffect(() => {
    const root = window.document.documentElement
    root.lang = language
    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
      root.classList.remove('light', 'dark')
      root.classList.add(systemTheme)
    } else {
      root.classList.remove('light', 'dark')
      root.classList.add(theme)
    }
  }, [theme, language])

  useEffect(() => {
    const handleGlobalError = (event: ErrorEvent | PromiseRejectionEvent) => {
      const msg =
        (event instanceof ErrorEvent ? event.error?.message : event.reason?.message) ||
        'Что-то пошло не так'
      if (msg.includes('ResizeObserver')) return
      toast.error(msg)
    }
    window.addEventListener('error', handleGlobalError)
    window.addEventListener('unhandledrejection', handleGlobalError)
    return () => {
      window.removeEventListener('error', handleGlobalError)
      window.removeEventListener('unhandledrejection', handleGlobalError)
    }
  }, [])

  const handleOpenGuide = (key: string, title?: string, icon?: string) => {
    if (key) {
      addToHistory({ key, title: title || key, icon: icon || '' })
      push({ type: 'guide', id: key })
    }
  }

  const headerTitle = useMemo(() => {
    const path = location.pathname
    if (path === '/favorites') return 'Избранное'
    if (path === '/history') return 'История'
    if (path.startsWith('/category/')) {
      const catKey = path.replace('/category/', '')
      return cats?.find((c) => c.key === catKey)?.title || 'Гайды'
    }
    if (path.startsWith('/tag/')) {
      return `#${decodeURIComponent(path.replace('/tag/', ''))}`
    }
    return 'BlackRose'
  }, [location.pathname, cats])

  const isHome = location.pathname === '/'
  const isGuide = location.pathname.startsWith('/guide/')
  const fabVisible =
    location.pathname.startsWith('/category/') || isGuide || location.pathname.startsWith('/tag/')
  const fabLabel = isGuide ? 'Назад' : 'Категории'
  const logoSrc = `${import.meta.env.BASE_URL}app-icon.png`

  return (
    <div
      className="app-shell flex h-[100dvh] flex-col overflow-hidden bg-background text-foreground transition-all duration-500"
      data-testid="app-shell"
    >
      <header className="sticky top-0 z-40 flex h-16 items-center px-4 glass shrink-0">
        {!isHome && location.pathname !== '/admin' ? (
          <Header
            title={headerTitle}
            onBack={handleBack}
          />
        ) : (
          <div className="flex w-full items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center overflow-hidden rounded-2xl border border-border/10 bg-background shadow-lg shadow-primary/20">
                {!logoFailed ? (
                  <img
                    src={logoSrc}
                    alt="BlackRose"
                    className="size-full object-cover"
                    onError={() => setLogoFailed(true)}
                  />
                ) : (
                  <span className="text-lg font-black text-foreground">B</span>
                )}
              </div>
              <span className="text-xl font-black uppercase tracking-tighter">BlackRose</span>
            </div>
            <div className="flex items-center gap-2">
              {isAdmin ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-10 rounded-2xl border border-primary/30 px-3 text-[11px] font-black uppercase tracking-[0.1em] text-primary"
                  onClick={() => {
                    haptic.light?.()
                    push({ type: 'admin' })
                  }}
                >
                  Панель
                </Button>
              ) : !inTelegram ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-10 rounded-2xl border border-border/40 px-3 text-[11px] font-black uppercase tracking-[0.1em] text-foreground/70"
                  onClick={() => {
                    haptic.light?.()
                    sheet.present({ type: 'login' })
                  }}
                >
                  Вход
                </Button>
              ) : null}

              <Button
                variant="ghost"
                size="icon"
                className="size-10 rounded-2xl transition-all active:rotate-180"
                onClick={() => {
                  haptic.medium?.()
                  setTheme(theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light')
                  toast.success(
                    `Тема: ${theme === 'light' ? 'Тёмная' : theme === 'dark' ? 'Системная' : 'Светлая'}`
                  )
                }}
              >
                <div className="flex items-center justify-center p-2 rounded-xl bg-muted/40 transition-colors hover:bg-muted">
                  {theme === 'light' ? (
                    <svg className="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                      />
                    </svg>
                  ) : theme === 'dark' ? (
                    <svg className="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="size-5 text-primary"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"
                      />
                    </svg>
                  )}
                </div>
              </Button>
            </div>
          </div>
        )}
      </header>

      <div className="flex-1 overflow-y-auto overflow-x-hidden no-scrollbar">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="flex flex-col h-full"
          >




            <Suspense fallback={<ViewLoader />}>
              <Routes location={location} key={location.pathname}>
                <Route
                  path="/"
                  element={
                    <CategoriesView
                      onSelectCategory={(cat) => push({ type: 'category', id: cat.key })}
                      onSelectGuide={handleOpenGuide}
                      onCategoriesLoaded={setCats}
                      onTagClick={(tag: string) => push({ type: 'tag', tag })}
                    />
                  }
                />
                <Route
                  path="/category/:id"
                  element={<InnerGuidesView onSelectGuide={handleOpenGuide} cats={cats} />}
                />
                <Route
                  path="/guide/:id"
                  element={
                    <InnerGuideView
                      isFavorite={isFavorite}
                      onToggleFavorite={toggleFav}
                      onOpenGuide={handleOpenGuide}
                      onTagClick={(tag: string) => push({ type: 'tag', tag })}
                      onGuideLoaded={(g) =>
                        addToHistory({ key: g.key, title: g.title, icon: g.icon })
                      }
                    />
                  }
                />
                <Route
                  path="/tag/:tag"
                  element={<InnerTagResultsView onSelectGuide={handleOpenGuide} />}
                />
                <Route
                  path="/favorites"
                  element={
                    <FavoritesView
                      favorites={favorites}
                      onSelectGuide={handleOpenGuide}
                      onToggle={toggleFav}
                    />
                  }
                />
                <Route
                  path="/history"
                  element={<HistoryView history={history} onSelectGuide={handleOpenGuide} />}
                />
                <Route
                  path="/admin"
                  element={<AdminView onClose={() => push({ type: 'home' })} />}
                />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </motion.div>
        </AnimatePresence>
      </div>

      <FabButton
        visible={fabVisible}
        label={fabLabel}
        onBack={handleBack}
        onHoldComplete={() => sheet.present({ type: 'quickNav' })}
      />

      <Toaster
        position="top-center"
        toastOptions={{
          className:
            'glass-card text-foreground rounded-3xl p-4 font-bold shadow-2xl transition-all border-none scale-110',
          duration: 3000,
        }}
      />

      {sheet.item?.type === 'login' && (
        <Suspense fallback={null}>
          <AdminLoginModal
            onSuccess={() => {
              setIsAdmin(true)
              sheet.dismiss()
              push({ type: 'admin' })
            }}
            onClose={sheet.dismiss}
          />
        </Suspense>
      )}

      {sheet.item?.type === 'quickNav' && (
        <Suspense fallback={null}>
          <QuickNav
            categories={cats || []}
            onSelect={(cat) => {
              push({ type: 'category', id: cat.key })
              sheet.dismiss()
            }}
            onHome={() => {
              push({ type: 'home' })
              sheet.dismiss()
            }}
            onClose={sheet.dismiss}
          />
        </Suspense>
      )}
    </div>
  )
}

interface InnerGuidesViewProps {
  onSelectGuide: (key: string, title?: string, icon?: string) => void
  cats: import('@/features/categories').Category[] | null
}

const InnerGuidesView = ({ onSelectGuide, cats }: InnerGuidesViewProps) => {
  const { id } = useParams()
  const cat = cats?.find((c) => c.key === id)
  const category = { key: id!, title: cat?.title || 'Гайды', icon: cat?.icon }
  return <GuidesView category={category} onSelectGuide={onSelectGuide} />
}

interface InnerGuideViewProps {
  isFavorite: (key: string) => boolean
  onToggleFavorite: (guide: { key: string; title: string; icon: string }) => void
  onOpenGuide: (key: string, title?: string, icon?: string) => void
  onTagClick: (tag: string) => void
  onGuideLoaded: (g: { key: string; title: string; icon?: string }) => void
}

const InnerGuideView = ({
  onToggleFavorite,
  isFavorite,
  onOpenGuide,
  onTagClick,
  onGuideLoaded,
}: InnerGuideViewProps) => {
  const { id } = useParams()
  return (
    <GuideView
      guideKey={id!}
      isFavorite={isFavorite(id!)}
      onToggleFavorite={onToggleFavorite}
      onOpenGuide={onOpenGuide}
      onTagClick={onTagClick}
      onGuideLoaded={onGuideLoaded}
    />
  )
}

interface InnerTagResultsViewProps {
  onSelectGuide: (key: string, title?: string, icon?: string) => void
}

const InnerTagResultsView = ({ onSelectGuide }: InnerTagResultsViewProps) => {
  const { tag } = useParams()
  return <TagResultsView tag={tag!} onSelectGuide={onSelectGuide} />
}

export default App
