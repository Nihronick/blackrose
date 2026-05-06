import { FC } from 'react';
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiAddComment, apiDeleteComment, apiGetComments } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import {
  ChevronDown,
  Clock,
  MessageCircle,
  MessageSquare,
  Send,
  ShieldCheck,
  Trash2,
  User,
} from '@/lib/icons'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useEffect, useRef, useState } from 'react'

interface Comment {
  id: string
  name: string
  text: string
  created_at: string
  is_own: boolean
  is_admin?: boolean
}

function formatTime(iso: string) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = (now.getTime() - d.getTime()) / 1000
  if (diff < 60) return 'только что'
  if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`
  return d.toLocaleDateString('ru', { day: 'numeric', month: 'short' })
}

interface CommentsSectionProps {
  guideKey: string
}

export const CommentsSection: FC<CommentsSectionProps> = ({ guideKey }) => {
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(true)
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [open, setOpen] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const load = async () => {
    try {
      const res = await apiGetComments(guideKey)
      setComments((res.comments || []) as Comment[])
    } catch {
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (open) load()
  }, [open, guideKey])

  useEffect(() => {
    if (open && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [comments, open])

  const send = async () => {
    if (!text.trim() || sending) return
    setSending(true)
    haptic.light?.()
    try {
      await apiAddComment(guideKey, text.trim())
      setText('')
      await load()
      haptic.success?.()
    } catch (e) {
      haptic.error?.()
    } finally {
      setSending(false)
    }
  }

  const remove = async (id: string) => {
    if (!window.confirm('Удалить комментарий?')) return
    haptic.light?.()
    try {
      await apiDeleteComment(guideKey, id)
      setComments((c) => c.filter((x) => x.id !== id))
    } catch {}
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div className="flex flex-col w-full border border-border/10 rounded-[28px] overflow-hidden bg-card/20 backdrop-blur-sm transition-all duration-300">
      <button
        className={cn(
          'flex items-center gap-3 px-6 h-16 w-full text-left transition-all active:scale-[0.99]',
          open ? 'bg-muted/30 border-b border-border/5' : 'hover:bg-muted/20'
        )}
        onClick={() => {
          haptic.light?.()
          setOpen((o) => !o)
        }}
      >
        <div
          className={cn(
            'flex size-9 items-center justify-center rounded-xl transition-colors',
            open ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground/60'
          )}
        >
          <MessageCircle className="size-5" />
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-bold tracking-tight">Комментарии</span>
          <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/40">
            {comments.length > 0 ? `${comments.length} сообщений` : 'начни обсуждение'}
          </span>
        </div>

        <ChevronDown
          className={cn(
            'ml-auto size-5 text-muted-foreground/40 transition-transform duration-300',
            open && 'rotate-180 text-primary/60'
          )}
        />
      </button>

      {open && (
        <div className="flex flex-col animate-in slide-in-from-top-2 duration-300">
          <div
            ref={scrollRef}
            className="flex flex-col gap-4 p-6 max-h-[400px] overflow-y-auto no-scrollbar scroll-smooth"
          >
            {loading ? (
              <div className="flex flex-col items-center justify-center py-12 gap-3 opacity-40">
                <div className="adm2-spinner" />
                <span className="text-[10px] font-black uppercase tracking-widest">
                  Загрузка...
                </span>
              </div>
            ) : comments.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center gap-4 opacity-20">
                <MessageSquare className="size-12" />
                <div className="text-sm font-bold">Будьте первым!</div>
              </div>
            ) : (
              comments.map((c) => (
                <div
                  key={c.id}
                  className={cn(
                    'flex flex-col gap-2 max-w-[85%] animate-in fade-in duration-300',
                    c.is_own ? 'self-end items-end' : 'self-start'
                  )}
                >
                  <div className={cn('flex items-center gap-2', c.is_own && 'flex-row-reverse')}>
                    <div
                      className={cn(
                        'flex size-7 items-center justify-center rounded-lg text-[9px] font-black shadow-sm',
                        c.is_own
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground'
                      )}
                    >
                      {getInitials(c.name)}
                    </div>
                    <span className="text-[11px] font-bold text-foreground/60">{c.name}</span>
                    <span className="text-[9px] font-medium text-muted-foreground/40">
                      {formatTime(c.created_at)}
                    </span>
                    {c.is_admin && (
                      <Badge
                        variant="outline"
                        className="h-4 px-1.5 text-[8px] font-black uppercase tracking-tighter border-primary/20 bg-primary/5 text-primary"
                      >
                        <ShieldCheck className="size-2.5 mr-1" />
                        Admin
                      </Badge>
                    )}
                  </div>

                  <div className="group relative">
                    <div
                      className={cn(
                        'px-4 py-2.5 rounded-2xl text-sm leading-relaxed shadow-sm',
                        c.is_own
                          ? 'bg-primary text-primary-foreground rounded-tr-none'
                          : 'bg-muted/80 text-foreground rounded-tl-none border border-border/5'
                      )}
                    >
                      {c.text}
                    </div>

                    {c.is_own && (
                      <button
                        className="absolute -left-8 top-1/2 -translate-y-1/2 p-2 text-muted-foreground/20 hover:text-destructive opacity-0 group-hover:opacity-100 transition-all active:scale-90"
                        onClick={() => remove(c.id)}
                      >
                        <Trash2 className="size-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Input Row */}
          <div className="p-4 bg-muted/20 border-t border-border/10">
            <div className="flex gap-2 p-1.5 bg-background rounded-2xl shadow-inner ring-1 ring-border/5 focus-within:ring-primary/20 transition-all">
              <Input
                ref={inputRef}
                className="h-10 border-none bg-transparent shadow-none focus-visible:ring-0 text-sm font-medium"
                placeholder="Ваш комментарий..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                maxLength={1000}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    send()
                  }
                }}
              />
              <Button
                className="size-10 rounded-xl px-0 shrink-0 shadow-lg shadow-primary/20 transition-all active:scale-90"
                onClick={send}
                disabled={!text.trim() || sending}
              >
                {sending ? (
                  <div className="adm2-spinner adm2-spinner-sm" />
                ) : (
                  <Send className="size-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
