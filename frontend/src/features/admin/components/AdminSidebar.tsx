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
          'fixed inset-y-0 left-0 z-50 w-72 bg-card border-r border-border/10 flex flex-col transition-transform duration-300 sm:relative sm:translate-x-0 shadow-2xl sm:shadow-none',
          open ? 'translate-x-0' : '-translate-x-full'
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
            onClick={onClose}
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
          {tabs.map((t) => (
            <button
              key={t.id}
              className={cn(
                'w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all duration-200 group relative',
                tab === t.id
                  ? 'bg-primary text-primary-foreground shadow-xl shadow-primary/10'
                  : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground hover:translate-x-1'
              )}
              onClick={() => onTabChange(t.id)}
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
            </button>
          ))}
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
