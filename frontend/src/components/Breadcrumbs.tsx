import { ChevronRight, Home } from '@/lib/icons'
import { useAppNavigation } from '@/lib/navigation'
import type { FC } from 'react'

export interface BreadcrumbItem {
  label: string
  route?: { type: string; id?: string }
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
}

export const Breadcrumbs: FC<BreadcrumbsProps> = ({ items }) => {
  const { push } = useAppNavigation()

  return (
    <nav className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium mb-4 overflow-x-auto no-scrollbar py-1">
      <button
        onClick={() => push({ type: 'home' })}
        className="flex items-center gap-1 hover:text-foreground transition-colors cursor-pointer shrink-0 font-heading uppercase text-[11px] font-bold"
      >
        <Home className="size-3.5 text-rose-400" />
        <span>Главная</span>
      </button>

      {items.map((item, index) => {
        const isLast = index === items.length - 1
        return (
          <div key={index} className="flex items-center gap-1.5 shrink-0">
            <ChevronRight className="size-3 text-muted-foreground/40" />
            {isLast || !item.route ? (
              <span className="text-foreground font-bold truncate max-w-[200px] text-[11px] font-heading uppercase">
                {item.label}
              </span>
            ) : (
              <button
                onClick={() => push(item.route as Parameters<typeof push>[0])}
                className="hover:text-foreground transition-colors cursor-pointer text-[11px] font-heading font-bold uppercase"
              >
                {item.label}
              </button>
            )}
          </div>
        )
      })}
    </nav>
  )
}
