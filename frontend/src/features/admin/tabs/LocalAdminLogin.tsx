import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { haptic } from '@/lib/haptic'
import type { FC, FormEvent } from 'react'
import { useState } from 'react'

interface LocalAdminLoginProps {
  onSuccess: () => void
  onBack?: () => void
}

export const LocalAdminLogin: FC<LocalAdminLoginProps> = ({ onSuccess, onBack }) => {
  const [user, setUser] = useState('')
  const [pass, setPass] = useState('')
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setErr('')
    try {
      const res = await fetch((import.meta.env.VITE_API_URL ?? '') + '/api/auth/admin-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pass }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Ошибка авторизации')

      localStorage.setItem('br_jwt', data.token)
      localStorage.setItem(
        'br_user',
        JSON.stringify({
          id: data.user_id,
          first_name: data.first_name,
          is_admin: true,
          is_local_admin: true,
        })
      )
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
    <Card className="w-full p-6 border border-primary/20 glass-card rounded-[32px] shadow-2xl">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex flex-col items-center">
          <div className="flex size-14 items-center justify-center rounded-[20px] bg-primary shadow-xl shadow-primary/20 text-white font-black text-xl tracking-tighter mb-4">
            BR
          </div>
          <h2 className="text-lg font-black tracking-tight mb-1 font-heading text-foreground">Вход в систему</h2>
          <p className="text-xs text-center text-muted-foreground/80 font-medium leading-relaxed max-w-[220px]">
            Доступ только для администраторов BlackRose
          </p>
        </div>

        <div className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label
              htmlFor="admin-login-input"
              className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 ml-1 font-heading"
            >
              Логин
            </label>
            <Input
              id="admin-login-input"
              className="h-11 rounded-2xl border border-border/20 bg-muted/30 font-bold text-sm focus-visible:bg-background focus-visible:ring-primary/20"
              placeholder="Введите логин..."
              value={user}
              onChange={(e) => setUser(e.target.value)}
              autoComplete="username"
            />
          </div>
          <div className="space-y-1.5">
            <label
              htmlFor="admin-pass-input"
              className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 ml-1 font-heading"
            >
              Пароль
            </label>
            <Input
              id="admin-pass-input"
              type="password"
              className="h-11 rounded-2xl border border-border/20 bg-muted/30 font-bold text-sm focus-visible:bg-background focus-visible:ring-primary/20"
              placeholder="••••••••"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
              autoComplete="current-password"
            />
          </div>
        </div>

        {err && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-2xl text-xs font-bold text-destructive text-center animate-in zoom-in-95">
            {err}
          </div>
        )}

        <div className="space-y-3 pt-2">
          <Button
            type="submit"
            className="h-12 w-full rounded-2xl font-black uppercase tracking-wider text-xs shadow-xl shadow-primary/20 transition-all active:scale-[0.98] font-heading cursor-pointer"
            disabled={loading || !user || !pass}
          >
            {loading ? <div className="adm2-spinner adm2-spinner-sm" /> : 'Подтвердить вход'}
          </Button>

          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="w-full py-2 text-xs font-bold text-primary hover:underline transition-all font-heading"
            >
              Вернуться назад
            </button>
          )}
        </div>
      </form>
    </Card>
  )
}
