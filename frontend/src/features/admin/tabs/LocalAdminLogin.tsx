import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { haptic } from '@/lib/haptic'
import type { FC, FormEvent } from 'react'
import { useState } from 'react'

import { useAppStore } from '@/store'

interface LocalAdminLoginProps {
  onSuccess: () => void
  onBack?: () => void
}

export const LocalAdminLogin: FC<LocalAdminLoginProps> = ({ onSuccess, onBack }) => {
  const [user, setUser] = useState('')
  const [pass, setPass] = useState('')
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)
  const { setIsAdmin } = useAppStore()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setErr('')
    try {
      let data: { token: string; user_id?: number; first_name?: string; detail?: string }
      if (user === 'emergency' || pass.startsWith('BlackRose_') || pass.length > 25) {
        const res = await fetch(
          (import.meta.env.VITE_API_URL ?? '') + '/api/auth/emergency-login',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ emergency_key: pass || user }),
          }
        )
        data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Ошибка аварийной авторизации')
      } else {
        const res = await fetch((import.meta.env.VITE_API_URL ?? '') + '/api/auth/admin-login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: user, password: pass }),
        })
        data = await res.json()
        if (!res.ok) throw new Error(data.detail || 'Ошибка авторизации')
      }

      localStorage.setItem('br_jwt', data.token)
      localStorage.setItem(
        'br_user',
        JSON.stringify({
          id: data.user_id || 7215567457,
          first_name: data.first_name || 'Project Lead',
          is_admin: true,
          is_local_admin: true,
        })
      )
      setIsAdmin(true)
      haptic.success?.()
      onSuccess()
    } catch (ex) {
      const err = ex instanceof Error ? ex : new Error(String(ex))
      setErr(err.message)
      haptic.light?.()
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full p-8 border border-rose-500/30 bg-card/90 backdrop-blur-2xl rounded-[32px] shadow-2xl shadow-rose-950/50 text-foreground">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex flex-col items-center">
          <div className="flex size-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-rose-800 to-rose-600 text-white shadow-xl shadow-rose-950/50 border border-white/10 font-black text-xl tracking-tighter mb-4">
            BR
          </div>
          <h2 className="text-xl font-black tracking-tight mb-1 font-heading text-foreground uppercase">
            Авторизация Администратора
          </h2>
          <p className="text-xs text-center text-muted-foreground font-medium leading-relaxed max-w-[240px]">
            Вход в защищённую панель управления BlackRose
          </p>
        </div>

        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label
              htmlFor="admin-login-input"
              className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1 font-heading"
            >
              Логин
            </label>
            <Input
              id="admin-login-input"
              className="h-12 rounded-2xl border border-rose-500/20 bg-background/80 font-semibold text-sm focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-rose-500/40 focus-visible:border-rose-500/50 text-foreground"
              placeholder="Введите логин..."
              value={user}
              onChange={(e) => setUser(e.target.value)}
              autoComplete="username"
            />
          </div>
          <div className="space-y-1.5">
            <label
              htmlFor="admin-pass-input"
              className="text-[10px] font-black uppercase tracking-widest text-muted-foreground ml-1 font-heading"
            >
              Пароль
            </label>
            <Input
              id="admin-pass-input"
              type="password"
              className="h-12 rounded-2xl border border-rose-500/20 bg-background/80 font-semibold text-sm focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-rose-500/40 focus-visible:border-rose-500/50 text-foreground"
              placeholder="••••••••"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
              autoComplete="current-password"
            />
          </div>
        </div>

        {err && (
          <div className="p-3 bg-destructive/15 border border-destructive/30 rounded-2xl text-xs font-bold text-destructive text-center animate-in zoom-in-95 font-heading">
            {err}
          </div>
        )}

        <div className="space-y-3 pt-2">
          <Button
            type="submit"
            className="rose-glow-btn h-14 w-full text-xs uppercase font-heading cursor-pointer"
            disabled={loading || !user || !pass}
          >
            {loading ? <div className="adm2-spinner adm2-spinner-sm" /> : 'Подтвердить Вход'}
          </Button>

          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="w-full py-2 text-xs font-bold text-rose-400 hover:underline transition-all font-heading"
            >
              Вернуться назад
            </button>
          )}
        </div>
      </form>
    </Card>
  )
}
