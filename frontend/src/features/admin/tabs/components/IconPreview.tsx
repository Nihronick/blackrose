import { normalizeUrl } from '@/lib/utils'
import type { FC } from 'react'
import type React from 'react'

export interface IconPreviewProps {
  url?: string
}

export const IconPreview: FC<IconPreviewProps> = ({ url }) => {
  if (!url)
    return (
      <div className="flex size-9 items-center justify-center rounded-xl bg-muted text-[10px] font-bold text-muted-foreground/40">
        ?
      </div>
    )
  return (
    <div className="flex size-9 items-center justify-center rounded-xl bg-muted/30 overflow-hidden ring-1 ring-border/5">
      <img
        src={normalizeUrl(url)}
        alt=""
        className="size-7 object-contain"
        onError={(e) => {
          ;(e.target as HTMLImageElement).style.display = 'none'
        }}
      />
    </div>
  )
}
