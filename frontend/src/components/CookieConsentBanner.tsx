import { haptic } from '@/lib/haptic'
import { Shield, X } from '@/lib/icons'
import { AnimatePresence, motion } from 'framer-motion'
import { type FC, useEffect, useState } from 'react'

const STORAGE_CONSENT_KEY = 'blackrose_cookie_consent'

export const CookieConsentBanner: FC = () => {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    try {
      const consent = localStorage.getItem(STORAGE_CONSENT_KEY)
      if (!consent) {
        // Show after 1.5s delay for smooth entrance
        const t = setTimeout(() => setVisible(true), 1500)
        return () => clearTimeout(t)
      }
    } catch {}
  }, [])

  const handleAccept = () => {
    haptic.medium()
    try {
      localStorage.setItem(STORAGE_CONSENT_KEY, 'accepted')
    } catch {}
    setVisible(false)
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 50, scale: 0.95 }}
          transition={{ duration: 0.3 }}
          className="fixed bottom-20 sm:bottom-6 left-4 right-4 max-w-xl mx-auto z-50 p-4 rounded-3xl bg-card/95 border border-rose-500/30 backdrop-blur-2xl shadow-2xl shadow-rose-950/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
        >
          <div className="flex items-start gap-3">
            <div className="size-9 rounded-2xl bg-primary/20 text-primary flex items-center justify-center shrink-0 mt-0.5 border border-primary/30">
              <Shield className="size-4" />
            </div>
            <div className="text-xs text-foreground/90 leading-relaxed">
              <p className="font-bold text-foreground font-heading">
                Защита данных и конфиденциальность (152-ФЗ / GDPR)
              </p>
              <p className="text-[11px] text-muted-foreground mt-0.5">
                Мы используем LocalStorage исключительно для сохранения ваших закладок, истории
                чтения и тем оформления.{' '}
                <a href="/legal" className="text-primary underline hover:text-rose-400">
                  Подробнее в политике
                </a>
                .
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto shrink-0 justify-end">
            <button
              onClick={handleAccept}
              className="w-full sm:w-auto px-5 py-2 rounded-2xl bg-primary text-white text-xs font-bold font-heading uppercase tracking-wider hover:bg-primary/90 transition-all shadow-md shadow-rose-950/40 active:scale-95"
            >
              Принять
            </button>
            <button
              onClick={() => setVisible(false)}
              className="size-8 rounded-xl bg-muted/40 hover:bg-muted text-muted-foreground flex items-center justify-center shrink-0"
              aria-label="Закрыть"
            >
              <X className="size-4" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
