import { Button } from '@/components/ui/button'
import { LogOut, X } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type { ComponentType, FC } from 'react'

interface AdminTab {
  id: string
  label: string
  icon: ComponentType<{ className?: string }>
}

interface AdminSidebarProps {
  tab: string
  tabs: readonly AdminTab[]
  open: boolean
  onClose: () => void
  onTabChange: (id: string) => void
  onLogout: () => void
}

export const AdminSidebar: FC<AdminSidebarProps> = ({
  tab,
  tabs,
  open,
  onClose,
  onTabChange,
  onLogout,
}) => {
  return (
    <>
      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm sm:hidden animate-in fade-in duration-300"
          onClick={onClose}
        />
      )}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-72 shrink-0 bg-card/80 backdrop-blur-2xl border-r border-rose-500/20 flex flex-col transition-transform duration-300 sm:relative sm:translate-x-0 shadow-2xl sm:shadow-none',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="p-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-[14px] bg-gradient-to-tr from-rose-800 to-rose-600 text-white font-black text-lg tracking-tighter shadow-lg shadow-rose-950/50 border border-white/10">
              BR
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-black uppercase tracking-tighter font-heading text-foreground">BlackRose</span>
              <span className="text-[10px] font-black uppercase tracking-widest text-rose-400 font-mono leading-none">
                Admin Panel
              </span>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="sm:hidden rounded-full h-8 w-8"
            onClick={onClose}
          >
            <X className="size-4" />
          </Button>
        </div>

        <nav className="flex-1 px-4 space-y-1.5 overflow-y-auto no-scrollbar py-2">
          {tabs.map((t) => {
            const active = tab === t.id
            const Icon = t.icon
            return (
              <button
                key={t.id}
                onClick={() => {
                  onTabChange(t.id)
                  onClose()
                }}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-2xl text-xs font-black uppercase tracking-wider transition-all duration-200 text-left font-heading cursor-pointer',
                  active
                    ? 'bg-gradient-to-r from-rose-900/60 to-rose-950/80 text-rose-300 border border-rose-500/30 shadow-lg shadow-rose-950/40'
                    : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
                )}
              >
                <Icon className={cn('size-4 transition-transform duration-200', active ? 'scale-110 text-rose-400' : 'opacity-70')} />
                <span className="truncate">{t.label}</span>
              </button>
            )
          })}
        </nav>

        <div className="p-6 border-t border-border/5">
          <Button
            variant="ghost"
            className="w-full justify-start h-12 rounded-2xl gap-3 text-muted-foreground hover:text-destructive hover:bg-destructive/5 transition-all group"
            onClick={onLogout}
          >
            <div className="flex size-8 items-center justify-center rounded-xl bg-muted/50 group-hover:bg-destructive/10 transition-colors">
              <LogOut className="size-4 group-hover:-translate-x-0.5 transition-transform" />
            </div>
            <span className="text-sm font-bold tracking-tight">Выйти</span>
          </Button>
        </div>
      </aside>
    </>
  )
}
