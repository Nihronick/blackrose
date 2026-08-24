import { FabButton } from '@/components/FabButton'
import { Header } from '@/components/Header'
import { Button } from '@/components/ui/button'
import { useCategories } from '@/hooks/queries'
import { useAppEnv } from '@/hooks/useAppEnv'
import { useSheet } from '@/hooks/useSheet'
import { useTelegramBackButton } from '@/hooks/useTelegramBackButton'
import { haptic } from '@/lib/haptic'
import { Compass, History, Home, Shield, Star, User } from '@/lib/icons'
import { useAppNavigation } from '@/lib/navigation'
import { useAppStore } from '@/store'
import { AnimatePresence, MotionConfig, motion } from 'framer-motion'
import { type FC, type ReactNode, Suspense, lazy, useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Toaster, toast } from 'sonner'

const AdminLoginModal = lazy(() =>
  import('@/components/AdminLoginModal').then((m) => ({ default: m.AdminLoginModal }))
)
const UserAuthModal = lazy(() =>
  import('@/components/UserAuthModal').then((m) => ({ default: m.UserAuthModal }))
)
const QuickNav = lazy(() => import('@/components/QuickNav').then((m) => ({ default: m.QuickNav })))
const OnboardingView = lazy(() =>
  import('@/views/OnboardingView').then((m) => ({ default: m.OnboardingView }))
)
const CookieConsentBanner = lazy(() =>
  import('@/components/CookieConsentBanner').then((m) => ({ default: m.CookieConsentBanner }))
)

interface AppLayoutProps {
  children: ReactNode
}

type AppSheet = { type: 'login' } | { type: 'quickNav' }

export const AppLayout: FC<AppLayoutProps> = ({ children }) => {
  const location = useLocation()
  const { push } = useAppNavigation()
  const { isTMA } = useAppEnv()
  const { data: categoriesData } = useCategories()
  const { isAdmin, cats, theme, setTheme, setIsAdmin, setCats, hasOnboarded } = useAppStore()
  const { handleBack } = useTelegramBackButton()
  const sheet = useSheet<AppSheet>()
  const [logoFailed, setLogoFailed] = useState(false)
  const [warmingUp, setWarmingUp] = useState(false)

  useEffect(() => {
    const handleWarmup = (e: Event) => {
      const customEv = e as CustomEvent<{ warming: boolean }>
      setWarmingUp(!!customEv.detail?.warming)
    }
    window.addEventListener('hf_space_warmup', handleWarmup)
    return () => window.removeEventListener('hf_space_warmup', handleWarmup)
  }, [])

  useEffect(() => {
    if (categoriesData && Array.isArray(categoriesData)) {
      setCats(categoriesData)
    }
  }, [categoriesData, setCats])

  // Scroll restoration: Reset scroll top on route transition
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
    const scrollables = document.querySelectorAll('.view-scroll, .overflow-y-auto')
    scrollables.forEach((el) => {
      el.scrollTop = 0
    })
  }, [location.pathname])

  const isHome = location.pathname === '/'
  const isCategory = location.pathname.startsWith('/category/')
  const isTag = location.pathname.startsWith('/tag/')
  const fabVisible = isCategory || isTag
  const logoSrc = `${import.meta.env.BASE_URL}app-icon.png`

  // Sync Telegram WebApp Native BackButton with React Router
  useEffect(() => {
    const tg = (
      window as unknown as {
        Telegram?: {
          WebApp?: {
            BackButton?: {
              show: () => void
              hide: () => void
              onClick: (fn: () => void) => void
              offClick: (fn: () => void) => void
            }
          }
        }
      }
    )?.Telegram?.WebApp
    if (!tg?.BackButton) return

    if (location.pathname !== '/') {
      tg.BackButton.show()
      tg.BackButton.onClick(handleBack)
      return () => {
        tg.BackButton.offClick(handleBack)
      }
    }
    tg.BackButton.hide()
  }, [location.pathname, handleBack])

  const headerTitle = useMemo(() => {
    const path = location.pathname
    if (path === '/favorites') return 'Избранное'
    if (path === '/history') return 'История'
    if (path === '/admin') return 'Админ-панель'
    if (path === '/roadmap') return 'Дорожная карта'
    if (path === '/build') return 'Калькулятор билда'
    if (path === '/search') return 'Поиск'
    if (path === '/legal' || path === '/privacy' || path === '/terms' || path === '/dmca')
      return 'Правовая информация'
    if (path.startsWith('/category/')) {
      const id = path.split('/').pop()
      const cat = cats?.find((c) => c.key === id)
      return cat?.title || 'База знаний'
    }
    if (path.startsWith('/tag/')) return '#' + path.split('/').pop()
    if (path.startsWith('/guide/')) return 'Гайд'
    if (path === '/guilds') return 'Гильдии'
    if (path.startsWith('/guilds/')) return 'Состав гильдии'
    if (path === '/profile') return 'Профиль'
    return 'BlackRose'
  }, [location.pathname, cats])

  return (
    <MotionConfig reducedMotion="user">
      <div className="app-shell flex min-h-screen w-full flex-col bg-background text-foreground relative">
        {warmingUp && (
          <div className="bg-primary/20 border-b border-primary/30 px-4 py-2 text-center text-xs font-bold text-primary animate-pulse flex items-center justify-center gap-2 shrink-0 z-50">
            <div className="adm2-spinner adm2-spinner-sm" />
            <span>
              ☕ Сервер просыпается (бесплатный тариф HF), загрузка завершится через пару секунд...
            </span>
          </div>
        )}

        {!isHome && location.pathname !== '/admin' ? (
          <Header title={headerTitle} onBack={handleBack} />
        ) : (
          <header className="sticky top-0 z-40 flex items-center container-padding glass border-b border-border/10 shrink-0 safe-header pb-2">
            <div className="flex w-full items-center justify-between gap-4">
              <div
                className="flex items-center gap-3 cursor-pointer"
                onClick={() => push({ type: 'home' })}
              >
                <div className="flex size-10 items-center justify-center overflow-hidden rounded-2xl border border-border/20 bg-background shadow-lg shadow-primary/20">
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
                <span className="text-xl font-black uppercase tracking-normal text-foreground font-heading">
                  BlackRose
                </span>
              </div>

              {/* Desktop Navigation Links */}
              <nav className="hidden md:flex items-center gap-1 font-heading">
                {[
                  { label: 'Главная', route: { type: 'home' } as const, active: isHome },
                  {
                    label: 'Категории',
                    route: { type: 'categories' } as const,
                    active: location.pathname === '/categories',
                  },
                  {
                    label: 'Гильдии',
                    route: { type: 'guilds' } as const,
                    active: location.pathname.startsWith('/guilds'),
                  },
                  {
                    label: 'Билды',
                    route: { type: 'build' } as const,
                    active: location.pathname === '/build',
                  },
                  {
                    label: 'Дорожная карта',
                    route: { type: 'roadmap' } as const,
                    active: location.pathname === '/roadmap',
                  },
                  {
                    label: 'Избранное',
                    route: { type: 'favorites' } as const,
                    active: location.pathname === '/favorites',
                  },
                ].map((item) => (
                  <Button
                    key={item.label}
                    variant="ghost"
                    size="sm"
                    className={`h-9 px-3.5 rounded-xl font-black text-xs uppercase tracking-wider transition-all ${
                      item.active
                        ? 'bg-primary/15 text-primary shadow-sm border border-primary/20'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                    }`}
                    onClick={() => {
                      haptic.light()
                      push(item.route)
                    }}
                  >
                    {item.label}
                  </Button>
                ))}
              </nav>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-10 rounded-2xl group/compass"
                  onClick={() => {
                    haptic.light()
                    push({ type: 'roadmap' })
                  }}
                  aria-label="Дорожная карта"
                >
                  <Compass className="size-5 text-muted-foreground group-hover/compass:text-primary transition-all duration-300 group-hover/compass:rotate-45" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-10 rounded-2xl"
                  onClick={() => {
                    haptic.light()
                    push({ type: 'search' })
                  }}
                  aria-label="Поиск"
                >
                  <SearchIcon className="size-5 text-muted-foreground" />
                </Button>
                {isAdmin ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-10 rounded-2xl border border-primary/30 px-3 text-[11px] font-black uppercase tracking-[0.1em] text-primary shadow-sm"
                    onClick={() => {
                      haptic.light()
                      push({ type: 'admin' })
                    }}
                  >
                    Панель
                  </Button>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-10 rounded-2xl border border-border/40 px-3 text-[11px] font-black uppercase tracking-[0.1em] text-foreground/70"
                    onClick={() => {
                      haptic.light()
                      sheet.present({ type: 'login' })
                    }}
                  >
                    Вход
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-10 rounded-2xl hover:bg-muted"
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

        {/* Main Content Area */}
        <main
          className={`flex-1 overflow-y-auto overflow-x-hidden no-scrollbar ${['/', '/favorites', '/history', '/profile', '/guilds'].includes(location.pathname) ? 'pb-36 md:pb-8' : 'pb-16 md:pb-6'}`}
        >
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

        {/* Floating Premium Bottom Navigation Tab Bar (Mobile Only) */}
        {['/', '/favorites', '/history', '/profile', '/guilds'].includes(location.pathname) && (
          <div className="md:hidden fixed bottom-[calc(1rem+var(--safe-bottom))] left-1/2 -translate-x-1/2 z-40 w-[92%] max-w-[400px] nav-dock-glass px-4 pt-2.5 pb-[calc(0.75rem+var(--safe-bottom))] rounded-[28px] shadow-2xl shrink-0 select-none">
            <div className="flex w-full items-center justify-around">
              {[
                { path: '/', label: 'Главная', icon: Home, route: { type: 'home' } as const },
                {
                  path: '/favorites',
                  label: 'Избранное',
                  icon: Star,
                  route: { type: 'favorites' } as const,
                },
                {
                  path: '/guilds',
                  label: 'Гильдии',
                  icon: Shield,
                  route: { type: 'guilds' } as const,
                },
                {
                  path: '/history',
                  label: 'История',
                  icon: History,
                  route: { type: 'history' } as const,
                },
                {
                  path: '/profile',
                  label: 'Профиль',
                  icon: User,
                  route: { type: 'profile' } as const,
                },
              ].map((tab) => {
                const Icon = tab.icon
                const isActive = location.pathname === tab.path
                return (
                  <button
                    key={tab.path}
                    type="button"
                    role="tab"
                    aria-selected={isActive}
                    aria-label={tab.label}
                    className={`flex flex-col items-center gap-1.5 py-1 px-3 rounded-2xl transition-all duration-300 relative ${
                      isActive
                        ? 'text-primary'
                        : 'text-muted-foreground/60 hover:text-foreground/80'
                    }`}
                    onClick={() => {
                      haptic.light()
                      push(tab.route)
                    }}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="active-tab"
                        className="absolute inset-0 bg-primary/10 rounded-2xl -z-10"
                        transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                      />
                    )}
                    <Icon
                      className={`size-5 transition-transform duration-300 ${isActive ? 'scale-110 stroke-[2.5px]' : 'scale-100'}`}
                    />
                    <span className="text-[10px] font-black uppercase tracking-wider font-heading leading-normal">
                      {tab.label}
                    </span>
                  </button>
                )
              })}
            </div>
          </div>
        )}

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
            <UserAuthModal
              onSuccess={() => {
                sheet.dismiss()
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

        {/* Global Footer with Fan Disclaimer, 12+ Rating, and Legal Links */}
        {location.pathname !== '/admin' && (
          <footer className="w-full border-t border-border/10 bg-card/40 backdrop-blur-md py-8 px-4 text-center mt-auto select-none">
            <div className="max-w-4xl mx-auto space-y-3">
              <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-muted-foreground/80 font-medium">
                <a href="/legal" className="hover:text-primary transition-colors">
                  Правовая информация (152-ФЗ / GDPR)
                </a>
                <span>•</span>
                <a href="/terms" className="hover:text-primary transition-colors">
                  Пользовательское соглашение
                </a>
                <span>•</span>
                <a href="/disclaimer" className="hover:text-primary transition-colors">
                  Дисклеймер
                </a>
                <span>•</span>
                <a href="/dmca" className="hover:text-primary transition-colors">
                  DMCA / Правообладатели
                </a>
              </div>

              <p className="text-[11px] text-muted-foreground/60 leading-relaxed max-w-2xl mx-auto">
                BlackRose — независимая некоммерческая база знаний и сообщество по игре{' '}
                <strong>Slayer Legend</strong>. Все права на игровые ассеты, товарные знаки и
                названия принадлежат <strong>GEAR2PLAY Co., Ltd.</strong> Проект не аффилирован с
                разработчиками игры. Возрастная маркировка: <strong>12+</strong>.
              </p>
            </div>
          </footer>
        )}

        {/* Cookie / LocalStorage Consent Banner */}
        <Suspense fallback={null}>
          <CookieConsentBanner />
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
