import { ExportImport } from '@/components/ExportImport'
import { IconLibrary } from '@/components/IconLibrary'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import {
  CategoriesTab,
  DashboardTab,
  DiscordLabTab,
  GuidesTab,
  HistoryTab,
  LocalAdminLogin,
  MediaTab,
} from '@/features/admin/AdminTabs'
import { AdminSidebar } from '@/features/admin/components/AdminSidebar'
import { apiFetch } from '@/lib/api'
import { GuildsTab } from '@/features/admin/GuildsTab'
import {
  AlertCircle,
  BarChart3,
  Beaker,
  ChevronRight,
  Download,
  FileText,
  Film,
  History,
  LayoutGrid,
  LogOut,
  Menu,
  Palette,
  Shield,
  ShieldCheck,
  X,
} from '@/lib/icons'
import type { Category, Guide } from '@/lib/types'
import { cn } from '@/lib/utils'
import { type ComponentType, type FC, Suspense, useCallback, useEffect, useState } from 'react'

interface AdminViewProps {
  onClose: () => void
}

interface AdminTab {
  id: string
  label: string
  title: string
  icon: ComponentType<{ className?: string }>
}

const TABS: readonly AdminTab[] = [
  { id: 'dash', label: 'Обзор', title: 'Системная панель', icon: BarChart3 },
  { id: 'guilds', label: 'Гильдии', title: 'Управление гильдиями', icon: Shield },
  { id: 'guides', label: 'Гайды', title: 'Управление гайдами', icon: FileText },
  { id: 'categories', label: 'Категории', title: 'Структура контента', icon: LayoutGrid },
  { id: 'media', label: 'Медиа', title: 'Библиотека файлов', icon: Film },
  { id: 'icons', label: 'Иконки', title: 'Библиотека стилей', icon: Palette },
  { id: 'history', label: 'История', title: 'Лог изменений', icon: History },
  { id: 'discord', label: 'Discord Lab', title: 'Синхронизация Slayerpedia', icon: Beaker },
  { id: 'export', label: 'Данные', title: 'Импорт и экспорт', icon: Download },
] as const

type TabId = (typeof TABS)[number]['id']

function TabSpinner() {
  return (
    <div className="flex h-60 items-center justify-center">
      <div className="adm2-spinner" />
    </div>
  )
}

export const AdminView: FC<AdminViewProps> = ({ onClose }) => {
  const [tab, setTab] = useState<TabId>('dash')
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [importedGuide, setImportedGuide] = useState<Guide | null>(null)

  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent).detail
      if (detail?.guide) {
        setImportedGuide(detail.guide)
        setTab('guides')
      }
    }
    window.addEventListener('blackrose:import:guide', handler)
    return () => window.removeEventListener('blackrose:import:guide', handler)
  }, [])

  const load = useCallback(async () => {
    setError(null)
    setLoading(true)
    try {
      const cats = await apiFetch<Category[]>('/api/admin/categories')
      setCategories(cats)
    } catch (e: unknown) {
      const isAuth =
        e instanceof Error &&
        (e.message === 'ACCESS_DENIED' || e.message?.includes('прав администратора'))
      setError(isAuth ? 'auth' : e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background animate-in fade-in duration-500">
        <div className="flex flex-col items-center gap-4">
          <div className="adm2-spinner size-12" />
          <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/40 animate-pulse">
            Инициализация...
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/95 backdrop-blur-2xl animate-in fade-in duration-300">
        <div className="w-full max-w-md space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-primary/10 rounded-2xl text-primary border border-primary/20 shadow-inner">
                <ShieldCheck className="size-6" />
              </div>
              <div>
                <h1 className="text-base font-black tracking-tight uppercase font-heading">Доступ ограничен</h1>
                <p className="text-[11px] font-bold text-muted-foreground/70">Административная панель BlackRose</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="rounded-full hover:bg-muted" onClick={onClose}>
              <X className="size-5" />
            </Button>
          </div>

          {error === 'auth' ? (
            <LocalAdminLogin onSuccess={() => window.location.reload()} />
          ) : (
            <Card className="p-6 border border-destructive/20 glass-card rounded-3xl text-center space-y-4">
              <AlertCircle className="size-10 text-destructive opacity-80 animate-bounce mx-auto" />
              <div className="text-sm font-bold text-foreground">{error}</div>
              <Button variant="default" className="rounded-2xl h-11 px-8 font-bold bg-primary text-primary-foreground font-heading" onClick={load}>
                Попробовать снова
              </Button>
            </Card>
          )}
        </div>
      </div>
    )
  }

  // Active tab metadata
  const activeTab = TABS.find((t) => t.id === tab)

  return (
    <div className="fixed inset-0 z-50 flex bg-background overflow-hidden animate-in fade-in duration-500">
      <AdminSidebar
        tab={tab}
        tabs={TABS}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onTabChange={(id) => {
          setTab(id)
          setSidebarOpen(false)
        }}
        onLogout={onClose}
      />

      {/* Main View Area */}
      <main className="flex-1 flex flex-col min-w-0 bg-muted/5">
        {/* Dynamic Header */}
        <header className="sticky top-0 z-30 flex items-center justify-between h-20 px-6 bg-background/50 backdrop-blur-xl border-b border-border/10">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="sm:hidden -ml-2 rounded-xl h-10 w-10"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="size-6" />
            </Button>
            <div className="flex flex-col">
              <h1 className="text-lg font-bold tracking-tight">{activeTab?.title}</h1>
              <div className="flex items-center gap-2">
                <div className="size-1.5 rounded-full bg-green-500 animate-pulse" />
                <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/50">
                  Online System
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-muted/40 rounded-full border border-border/5">
              <div className="size-6 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                {activeTab && <activeTab.icon className="size-3.5" />}
              </div>
              <span className="text-[10px] font-black tracking-widest text-muted-foreground uppercase">
                {activeTab?.label}
              </span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full h-10 w-10 hover:bg-muted"
              onClick={onClose}
            >
              <X className="size-6" />
            </Button>
          </div>
        </header>

        {/* Content Container */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden no-scrollbar">
          <div className="max-w-[1400px] mx-auto p-6 md:p-8">
            <Suspense fallback={<TabSpinner />}>
              <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                {activeTab?.id === 'dash' && <DashboardTab />}
                {activeTab?.id === 'guilds' && <GuildsTab />}
                {activeTab?.id === 'guides' && (
                  <GuidesTab
                    categories={categories}
                    importedGuide={importedGuide || undefined}
                    onImportProcessed={() => setImportedGuide(null)}
                  />
                )}
                {activeTab?.id === 'categories' && (
                  <CategoriesTab categories={categories} onReload={load} />
                )}
                {activeTab?.id === 'media' && <MediaTab />}
                {activeTab?.id === 'icons' && <IconLibrary />}
                {activeTab?.id === 'history' && <HistoryTab />}
                {activeTab?.id === 'discord' && <DiscordLabTab />}
                {tab === 'export' && <ExportImport />}
              </div>
            </Suspense>
          </div>
        </div>
      </main>
    </div>
  )
}
