import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { handleTelegramLogin } from '@/lib/auth'
import { ExternalLink, ShieldCheck } from '@/lib/icons'
import type React from 'react'
import { useEffect, useRef, useState } from 'react'

const BOT_NAME = import.meta.env.VITE_BOT_NAME || 'blackrosesl1_bot'
const BASE = import.meta.env.VITE_API_URL ?? ''

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

interface WebLoginViewProps {
  onSuccess?: (result: unknown) => void
}

export const WebLoginView: React.FC<WebLoginViewProps> = ({ onSuccess }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!containerRef.current)
      return // Регистрируем callback глобально (виджет вызывает window.onTelegramAuth)
    ;(window as unknown as { onTelegramAuth: (user: TelegramUser) => void }).onTelegramAuth =
      async (user: TelegramUser) => {
        setLoading(true)
        setError('')
        try {
          const result = await handleTelegramLogin(user, BASE)
          onSuccess?.(result)
        } catch (e: unknown) {
          setError(e instanceof Error ? e.message : 'Ошибка входа')
        } finally {
          setLoading(false)
        }
      }

    // Вставляем скрипт виджета
    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.setAttribute('data-telegram-login', BOT_NAME)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-onauth', 'onTelegramAuth(user)')
    script.setAttribute('data-request-access', 'write')
    script.async = true
    containerRef.current.appendChild(script)

    return () => {
      ;(window as unknown as { onTelegramAuth?: (user: TelegramUser) => void }).onTelegramAuth =
        undefined
    }
  }, [onSuccess])

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-background animate-in fade-in duration-500 min-h-screen">
      <Card className="w-full max-w-sm p-12 flex flex-col items-center text-center space-y-8 border-none bg-card/40 backdrop-blur-xl shadow-2xl rounded-[40px] ring-1 ring-border/5">
        <div className="flex flex-col items-center">
          <div className="flex size-20 items-center justify-center rounded-[28px] bg-primary shadow-2xl shadow-primary/30 text-white font-black text-3xl tracking-tighter mb-8 animate-in zoom-in-0 duration-500">
            BR
          </div>
          <h2 className="text-2xl font-black tracking-tight uppercase mb-3">BlackRose Guides</h2>
          <p className="text-sm font-medium text-muted-foreground/70 leading-relaxed max-w-[240px]">
            Энциклопедия гильдии. Используйте Telegram для безопасного входа.
          </p>
        </div>

        <div className="w-full flex flex-col items-center gap-6 min-h-[64px]">
          {loading ? (
            <div className="flex flex-col items-center gap-3">
              <div className="adm2-spinner" />
              <span className="text-[10px] font-black uppercase tracking-widest text-primary animate-pulse">
                Верификация...
              </span>
            </div>
          ) : (
            <div ref={containerRef} className="animate-in fade-in zoom-in-95 duration-300" />
          )}

          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-2xl text-[11px] font-bold text-destructive animate-in shake-in">
              {error}
            </div>
          )}
        </div>

        <div className="w-full h-[1px] bg-border/10" />

        <div className="space-y-4">
          <div className="flex items-center justify-center gap-2 text-muted-foreground/40">
            <ShieldCheck className="size-4" />
            <span className="text-[10px] font-black uppercase tracking-widest leading-none">
              Safe Authorization
            </span>
          </div>

          <a
            href={`https://t.me/${BOT_NAME}`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 justify-center text-[11px] font-bold text-primary/70 hover:text-primary transition-colors group"
          >
            <span>Или открыть в боте @{BOT_NAME}</span>
            <ExternalLink className="size-3 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
          </a>
        </div>
      </Card>
    </div>
  )
}
