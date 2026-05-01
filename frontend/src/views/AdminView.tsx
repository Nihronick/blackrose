import { ExportImport } from '@/components/ExportImport'
import { IconLibrary } from '@/components/IconLibrary'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import {
  CategoriesTab,
  DashboardTab,
  GuidesTab,
  HistoryTab,
  LocalAdminLogin,
  MediaTab,
  DiscordLabTab,
} from '@/features/admin/AdminTabs'
import { apiFetch } from '@/lib/api'
import type { Category } from '@/lib/types'
import { isTelegram } from '@/lib/auth'
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
  ShieldCheck,
  X,
} from '@/lib/icons'
import { cn } from '@/lib/utils'
import type React from 'react'
import { Suspense, useCallback, useEffect, useState } from 'react'

interface AdminViewProps {
  onClose: () => void
}

const TABS = [
  { id: 'dash', label: 'Обзор', title: 'Системная панель', icon: BarChart3 },
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

export const AdminView: React.FC<AdminViewProps> = ({ onClose }) => {
  const [tab, setTab] = useState<TabId>('dash')
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [importedGuide, setImportedGuide] = useState<any>(null)

  useEffect(() => {
    const handler = (e: any) => {
      setImportedGuide(e.detail.guide)
      setTab('guides')
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
      <div className="fixed inset-0 z-50 bg-background overflow-y-auto pt-12 pb-20 px-6 animate-in fade-in duration-300">
        <div className="max-w-md mx-auto space-y-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-destructive/10 rounded-2xl text-destructive shadow-sm shadow-destructive/10">
                <ShieldCheck className="size-6" />
              </div>
              <h1 className="text-xl font-black tracking-tight uppercase">Доступ ограничен</h1>
            </div>
            <Button variant="ghost" size="icon" className="rounded-full" onClick={onClose}>
              <X className="size-6" />
            </Button>
          </div>

          <Card className="p-6 border-none bg-card/50 shadow-xl ring-1 ring-border/5 space-y-6">
            {error === 'auth' ? (
              <>
                <div className="space-y-2">
                  <div className="text-sm font-bold text-foreground/80 leading-relaxed">
                    Для доступа к панели управления необходимо войти через Telegram или локальный
                    аккаунт.
                  </div>
                  <div className="text-[11px] font-medium text-muted-foreground/60 leading-relaxed">
                    Команда в боте:{' '}
                    <code className="bg-muted px-1.5 py-0.5 rounded text-primary font-bold">
                      /admin
                    </code>
                  </div>
                </div>
                <div className="w-[1px] h-4 bg-border/20 mx-auto" />
                {!isTelegram() ? (
                  <LocalAdminLogin onSuccess={() => window.location.reload()} />
                ) : (
                  <div className="text-center p-4 bg-primary/5 rounded-2xl border border-primary/10">
                    <p className="text-xs font-bold text-primary italic">
                      Используйте команду /admin в боте для обновления прав
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col items-center text-center gap-4 py-4">
                <AlertCircle className="size-12 text-destructive opacity-40" />
                <div className="text-sm font-bold text-destructive">{error}</div>
                <Button variant="secondary" className="rounded-xl h-10 px-6" onClick={load}>
                  Попробовать снова
                </Button>
              </div>
            )}
          </Card>
        </div>
      </div>
    )
  }

  // Active tab metadata
  const activeTab = TABS.find((t) => t.id === tab)

  return (
    <div className="fixed inset-0 z-50 flex bg-background overflow-hidden animate-in fade-in duration-500">
      {/* Sidebar Overlay (Mobile) */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm sm:hidden animate-in fade-in duration-300"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-72 bg-card border-r border-border/10 flex flex-col transition-transform duration-300 sm:relative sm:translate-x-0 shadow-2xl sm:shadow-none',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="p-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-[14px] bg-primary text-primary-foreground font-black text-lg tracking-tighter shadow-lg shadow-primary/20">
              BR
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-black uppercase tracking-tighter">BlackRose</span>
              <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/40 leading-none">
                Admin Panel
              </span>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="sm:hidden rounded-full h-8 w-8"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="size-4" />
          </Button>
        </div>

        <nav className="flex-1 px-4 py-2 space-y-1 overflow-y-auto no-scrollbar">
          <div className="px-4 py-4">
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground/20">
              Навигация
            </h3>
          </div>
          {TABS.map((t) => (
            <button
              key={t.id}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all duration-200 group relative',
                tab === t.id
                  ? 'bg-primary text-primary-foreground shadow-xl shadow-primary/10'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground hover:translate-x-1'
              )}
              onClick={() => {
                setTab(t.id)
                setSidebarOpen(false)
              }}
            >
              <t.icon
                className={cn(
                  'size-5 transition-transform group-hover:scale-110',
                  tab === t.id
                    ? 'text-primary-foreground'
                    : 'text-muted-foreground/40 group-hover:text-primary/60'
                )}
              />
              <span className="text-sm font-bold tracking-tight">{t.label}</span>
              {tab === t.id && (
                <div className="absolute right-3 size-1.5 rounded-full bg-primary-foreground/40 animate-pulse" />
              )}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-border/5">
          <Button
            variant="ghost"
            className="w-full justify-start h-12 rounded-2xl gap-3 text-muted-foreground hover:text-destructive hover:bg-destructive/5 transition-all group"
            onClick={onClose}
          >
            <div className="flex size-8 items-center justify-center rounded-xl bg-muted/50 group-hover:bg-destructive/10 transition-colors">
              <LogOut className="size-4 group-hover:-translate-x-0.5 transition-transform" />
            </div>
            <span className="text-sm font-bold tracking-tight">Выйти</span>
          </Button>
        </div>
      </aside>

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
                {activeTab?.id === 'guides' && (
                  <GuidesTab 
                    categories={categories} 
                    importedGuide={importedGuide} 
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
