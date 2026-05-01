import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { haptic } from '@/lib/haptic'
import { Home } from '@/lib/icons'
import type React from 'react'

interface Category {
  key: string
  title: string
  icon?: string
}

interface QuickNavProps {
  categories: Category[]
  onSelect: (cat: Category) => void
  onHome: () => void
  onClose: () => void
}

/**
 * QuickNav refactored with shadcn/ui Sheet and Lucide icons.
 * Premium mobile-first search/navigation component.
 */
export const QuickNav: React.FC<QuickNavProps> = ({ categories, onSelect, onHome, onClose }) => {
  return (
    <Sheet open onOpenChange={onClose}>
      <SheetContent side="bottom" className="rounded-t-[32px] px-6 pb-12 pt-8">
        <SheetHeader className="mb-6">
          <SheetTitle className="text-left text-xs font-bold uppercase tracking-widest text-muted-foreground">
            Перейти в раздел
          </SheetTitle>
        </SheetHeader>

        <div className="flex flex-col gap-1">
          {categories.map((cat) => (
            <button
              key={cat.key}
              className="group flex items-center gap-4 rounded-2xl p-3 transition-all hover:bg-muted active:scale-95 active:bg-muted/80"
              onClick={() => {
                haptic.select()
                onSelect(cat)
              }}
            >
              <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-muted transition-colors group-hover:bg-background">
                {cat.icon ? (
                  <img
                    src={cat.icon}
                    alt=""
                    className="size-8 object-contain"
                    onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ) : (
                  <span className="text-xl">📁</span>
                )}
              </div>
              <span className="text-base font-semibold text-foreground tracking-tight">
                {cat.title}
              </span>
            </button>
          ))}

          <div className="my-3 h-px bg-border" />

          <button
            className="group flex items-center gap-4 rounded-2xl p-3 transition-all hover:bg-muted active:scale-95 active:bg-muted/80"
            onClick={() => {
              haptic.select()
              onHome()
            }}
          >
            <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg transition-transform group-hover:scale-110">
              <Home className="size-6" />
            </div>
            <span className="text-base font-bold text-foreground tracking-tight">Главное меню</span>
          </button>
        </div>
      </SheetContent>
    </Sheet>
  )
}
