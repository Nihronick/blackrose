import { FabButton } from '@/components/FabButton'
import { Header } from '@/components/Header'
import { Button } from '@/components/ui/button'
import { useAppEnv } from '@/hooks/useAppEnv'
import { useSheet } from '@/hooks/useSheet'
import { useTelegramBackButton } from '@/hooks/useTelegramBackButton'
import { haptic } from '@/lib/haptic'
import { useAppNavigation } from '@/lib/navigation'
import { useAppStore } from '@/store'
import { AnimatePresence, MotionConfig, motion } from 'framer-motion'
import { type FC, type ReactNode, Suspense, lazy, useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Toaster, toast } from 'sonner'

const AdminLoginModal = lazy(() =>
  import('@/components/AdminLoginModal').then((m) => ({ default: m.AdminLoginModal }))
)
const QuickNav = lazy(() => import('@/components/QuickNav').then((m) => ({ default: m.QuickNav })))
const GlobalSearch = lazy(() =>
  import('@/components/GlobalSearch').then((m) => ({ default: m.GlobalSearch }))
)

interface AppLayoutProps {
  children: ReactNode
}

type AppSheet = { type: 'login' } | { type: 'quickNav' }

export const AppLayout: FC<AppLayoutProps> = ({ children }) => {
  const location = useLocation()
  const { push } = useAppNavigation()
  const { isTMA } = useAppEnv()
  const { isAdmin, cats, theme, setTheme, setIsAdmin, setSearchOpen } = useAppStore()
  const { handleBack } = useTelegramBackButton()
  const sheet = useSheet<AppSheet>()
  const [logoFailed, setLogoFailed] = useState(false)

  const isHome = location.pathname === '/'
  const isCategory = location.pathname.startsWith('/category/')
  const isTag = location.pathname.startsWith('/tag/')
  const fabVisible = isCategory || isTag
  const logoSrc = `${import.meta.env.BASE_URL}app-icon.png`

  const headerTitle = useMemo(() => {
    const path = location.pathname
    if (path === '/favorites') return 'Избранное'
    if (path === '/history') return 'История'
    if (path === '/admin') return 'Админ-панель'
    if (path.startsWith('/category/')) {
      const id = path.split('/').pop()
      const cat = cats?.find((c) => c.key === id)
      return cat?.title || 'База знаний'
    }
    if (path.startsWith('/tag/')) return '#' + path.split('/').pop()
    if (path.startsWith('/guide/')) return 'Гайд'
    return 'BlackRose'
  }, [location.pathname, cats])

  return (
    <MotionConfig reducedMotion="user">
      <div className="app-shell flex h-[var(--tg-viewport-stable-height,100dvh)] flex-col overflow-hidden bg-background text-foreground">
        {!isHome && location.pathname !== '/admin' ? (
          <Header title={headerTitle} onBack={handleBack} />
        ) : (
          <header className="sticky top-0 z-40 flex h-16 items-center px-4 glass shrink-0">
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
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-10 rounded-2xl"
                  onClick={() => setSearchOpen(true)}
                >
                  <SearchIcon className="size-5 text-muted-foreground" />
                </Button>
                {isAdmin ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-10 rounded-2xl border border-primary/30 px-3 text-[11px] font-black uppercase tracking-[0.1em] text-primary"
                    onClick={() => push({ type: 'admin' })}
                  >
                    Панель
                  </Button>
                ) : !isTMA ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-10 rounded-2xl border border-border/40 px-3 text-[11px] font-black uppercase tracking-[0.1em] text-foreground/70"
                    onClick={() => sheet.present({ type: 'login' })}
                  >
                    Вход
                  </Button>
                ) : null}
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-10 rounded-2xl"
                  onClick={() => {
                    setTheme(theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light')
                  }}
                >
                  <ThemeIcon theme={theme} />
                </Button>
              </div>
            </div>
          </header>
        )}

        <main className="flex-1 overflow-y-auto overflow-x-hidden no-scrollbar">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col h-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </main>

        <FabButton
          visible={fabVisible}
          label="Навигация"
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

        <Suspense fallback={null}>
          <GlobalSearch />
        </Suspense>
      </div>
    </MotionConfig>
  )
}

const SearchIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
    />
  </svg>
)

const ThemeIcon = ({ theme }: { theme: string }) => {
  if (theme === 'light') return <SunIcon />
  if (theme === 'dark') return <MoonIcon />
  return <SystemIcon />
}

const SunIcon = () => (
  <svg className="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
    />
  </svg>
)

const MoonIcon = () => (
  <svg className="size-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
    />
  </svg>
)

const SystemIcon = () => (
  <svg className="size-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"
    />
  </svg>
)
