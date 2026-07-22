import { FC, ImgHTMLAttributes, useEffect, useState } from 'react'
import { normalizeUrl } from '@/lib/utils'

interface SmartImageProps extends ImgHTMLAttributes<HTMLImageElement> {
  src: string
  maxRetries?: number
  retryIntervalMs?: number
}

export const SmartImage: FC<SmartImageProps> = ({
  src,
  alt = '',
  className = '',
  maxRetries = 3,
  retryIntervalMs = 1500,
  ...props
}) => {
  const [currentSrc, setCurrentSrc] = useState(() => normalizeUrl(src))
  const [retries, setRetries] = useState(0)
  const [failed, setFailed] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setCurrentSrc(normalizeUrl(src))
    setRetries(0)
    setFailed(false)
    setLoading(true)
  }, [src])

  const handleError = () => {
    if (retries < maxRetries) {
      setTimeout(() => {
        setRetries((r) => r + 1)
        const clean = normalizeUrl(src)
        const sep = clean.includes('?') ? '&' : '?'
        setCurrentSrc(`${clean}${sep}_t=${Date.now()}`)
      }, retryIntervalMs)
    } else {
      setFailed(true)
      setLoading(false)
    }
  }

  const handleLoad = () => {
    setLoading(false)
    setFailed(false)
  }

  if (failed) {
    return (
      <div className={`flex items-center justify-center bg-muted/40 text-muted-foreground/40 rounded-xl p-2 text-[10px] font-bold uppercase tracking-wider ${className}`}>
        🖼️ Ошибка загрузки
      </div>
    )
  }

  return (
    <div className="relative inline-block overflow-hidden">
      {loading && (
        <div className="absolute inset-0 bg-muted/30 animate-pulse rounded-xl flex items-center justify-center">
          <div className="adm2-spinner adm2-spinner-sm" />
        </div>
      )}
      <img
        {...props}
        src={currentSrc}
        alt={alt}
        className={`${className} ${loading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
        onLoad={handleLoad}
        onError={handleError}
      />
    </div>
  )
}
