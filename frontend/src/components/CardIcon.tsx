import { cn, normalizeUrl } from '@/lib/utils'
import type React from 'react'

interface CardIconProps {
  url?: string
  size?: number
  placeholder?: string
  className?: string
}

/**
 * Portable CardIcon with support for premium shadcn-style layouts.
 */
export const CardIcon: React.FC<CardIconProps> = ({
  url,
  size = 48,
  placeholder = '📁',
  className,
}) => {
  return (
    <div
      className={cn(
        'flex shrink-0 items-center justify-center rounded-2xl bg-muted transition-colors',
        className
      )}
      style={{ width: size, height: size }}
    >
      {url ? (
        <img
          src={normalizeUrl(url)}
          alt=""
          width={size * 0.75}
          height={size * 0.75}
          className="object-contain"
          crossOrigin="anonymous"
          loading="lazy"
          onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      ) : (
        <span className="text-2xl">{placeholder}</span>
      )}
    </div>
  )
}

export default CardIcon
