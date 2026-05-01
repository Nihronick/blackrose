import { Button } from '@/components/ui/button'
import { X, ZoomIn } from '@/lib/icons'
import type React from 'react'
import { useEffect } from 'react'

interface LightboxProps {
  src: string
  onClose: () => void
}

export const Lightbox: React.FC<LightboxProps> = ({ src, onClose }) => {
  useEffect(() => {
    const fn = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', fn)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', fn)
      document.body.style.overflow = ''
    }
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 backdrop-blur-md animate-in fade-in duration-300 pointer-events-auto"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose()
      }}
    >
      <div className="absolute top-6 right-6 z-[110] flex gap-2">
        <Button
          variant="secondary"
          size="icon"
          className="rounded-full bg-white/10 text-white hover:bg-white/20 border-none backdrop-blur-xl"
          onClick={onClose}
        >
          <X className="size-6" />
        </Button>
      </div>

      <div className="relative max-w-[95vw] max-h-[95vh] flex items-center justify-center animate-in zoom-in-95 duration-500">
        <img
          src={src}
          alt=""
          className="max-w-full max-h-full object-contain shadow-2xl rounded-lg ring-1 ring-white/10"
          onClick={(e) => e.stopPropagation()}
        />

        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 bg-black/40 backdrop-blur-xl rounded-full border border-white/10 opacity-0 hover:opacity-100 transition-opacity">
          <div className="flex items-center gap-2 text-white/60 text-[10px] font-black uppercase tracking-widest">
            <ZoomIn className="size-3" />
            Full Resolution View
          </div>
        </div>
      </div>
    </div>
  )
}
