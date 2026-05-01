import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { haptic } from '@/lib/haptic'
import { AlertCircle, Loader2, Lock, User } from '@/lib/icons'
import type React from 'react'
import { useState } from 'react'

interface AdminLoginModalProps {
  onSuccess: () => void
  onClose: () => void
}

/**
 * AdminLoginModal refactored with shadcn/ui components and RemoteData.
 */
export const AdminLoginModal: React.FC<AdminLoginModalProps> = ({ onSuccess, onClose }) => {
  const [user, setUser] = useState('')
  const [pass, setPass] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

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

      haptic.success?.()
      onSuccess()
    } catch (ex) {
      const parsed = ex instanceof Error ? ex.message : 'Ошибка авторизации'
      setError(parsed)
      haptic.light?.()
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[400px] rounded-[32px] p-8">
        <DialogHeader className="mb-6 flex flex-col items-center gap-4">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg shadow-primary/20">
            <Lock className="size-7" />
          </div>
          <div className="text-center">
            <DialogTitle className="text-2xl font-black tracking-tight">Админ-панель</DialogTitle>
            <DialogDescription className="text-xs font-bold uppercase tracking-widest text-muted-foreground/60 mt-1">
              Авторизация
            </DialogDescription>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="flex flex-col gap-2">
            <div className="relative group/field">
              <User className="absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within/field:text-primary" />
              <Input
                className="h-12 border-none bg-muted/50 pl-11 text-base focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-primary/20"
                placeholder="Логин"
                value={user}
                onChange={(e) => setUser(e.target.value)}
                autoComplete="username"
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <div className="relative group/field">
              <Lock className="absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within/field:text-primary" />
              <Input
                className="h-12 border-none bg-muted/50 pl-11 text-base focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-primary/20"
                type="password"
                placeholder="Пароль"
                value={pass}
                onChange={(e) => setPass(e.target.value)}
                autoComplete="current-password"
                disabled={isLoading}
              />
            </div>
          </div>

          {error && (
            <Alert variant="destructive" className="bg-destructive/10 border-none text-destructive">
              <AlertCircle className="size-4" />
              <AlertDescription className="text-xs font-bold">{error}</AlertDescription>
            </Alert>
          )}

          <Button
            className="h-14 rounded-2xl text-base font-bold shadow-lg shadow-primary/20 mt-4 active:scale-95 transition-all"
            type="submit"
            disabled={isLoading || !user || !pass}
          >
            {isLoading ? <Loader2 className="size-5 animate-spin" /> : 'Войти'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
