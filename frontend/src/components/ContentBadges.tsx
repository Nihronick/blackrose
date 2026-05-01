import { Badge } from '@/components/ui/badge'
import { FileText, Film, ImageIcon as Image } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type React from 'react'

interface ContentBadgeProps {
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>
  label: string
  className?: string
}

const ItemBadge: React.FC<ContentBadgeProps> = ({ icon: Icon, label, className }) => (
  <Badge
    variant="secondary"
    className={cn(
      'h-5 gap-1.5 px-2 rounded-full border-none font-black text-[9px] uppercase tracking-wider bg-muted/40 text-muted-foreground/60 shadow-sm',
      className
    )}
  >
    <Icon className="size-2.5" />
    {label}
  </Badge>
)

interface ContentBadgesProps {
  hasPhoto?: boolean
  hasVideo?: boolean
  hasDocument?: boolean
}

export const ContentBadges: React.FC<ContentBadgesProps> = ({
  hasPhoto,
  hasVideo,
  hasDocument,
}) => {
  if (!hasPhoto && !hasVideo && !hasDocument) return null

  return (
    <div className="flex items-center gap-1.5">
      {hasPhoto && (
        <ItemBadge
          icon={Image}
          label="Фото"
          className="hover:bg-blue-500/10 hover:text-blue-500 transition-colors"
        />
      )}
      {hasVideo && (
        <ItemBadge
          icon={Film}
          label="Видео"
          className="hover:bg-red-500/10 hover:text-red-500 transition-colors"
        />
      )}
      {hasDocument && (
        <ItemBadge
          icon={FileText}
          label="Файл"
          className="hover:bg-green-500/10 hover:text-green-500 transition-colors"
        />
      )}
    </div>
  )
}
