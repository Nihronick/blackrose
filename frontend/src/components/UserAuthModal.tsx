import { apiEmergencyLogin } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { useAppNavigation } from '@/lib/navigation'
import { motion } from 'framer-motion'
import { KeyRound, Shield, Sparkles, User, X } from 'lucide-react'
import { type FC, useState } from 'react'
import { toast } from 'sonner'
import { Button } from './ui/button'
import { Input } from './ui/input'

interface UserAuthModalProps {
  onClose: () => void
  onSuccess?: () => void
}

export const UserAuthModal: FC<UserAuthModalProps> = ({ onClose, onSuccess }) => {
  const { push } = useAppNavigation()
  const [tab, setTab] = useState<'user' | 'emergency'>('user')
  const [nickname, setNickname] = useState('')
  const [emergencyKey, setEmergencyKey] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSaveProfile = () => {
    const trimmed = nickname.trim()
    if (!trimmed) {
      toast.error('Введите ваш никнейм в игре!')
      return
    }
    haptic.medium()
    setIsSubmitting(true)

    // Save to localStorage as player session
    localStorage.setItem('slayer_nickname', trimmed)

    toast.success(`С возвращением, ${trimmed}!`)
    setIsSubmitting(false)
    onSuccess?.()
    onClose()
  }

  const handleEmergencyLogin = async () => {
    const trimmed = emergencyKey.trim()
    if (!trimmed) {
      toast.error('Введите аварийный ключ администратора!')
      return
    }
    haptic.heavy()
    setIsSubmitting(true)
    try {
      const res = await apiEmergencyLogin(trimmed)
      if (res?.token) {
        localStorage.setItem('blackrose_jwt_token', res.token)
        localStorage.setItem('blackrose_is_admin', 'true')
        toast.success('Аварийный вход выполнен! Права Project Lead применены.')
        onSuccess?.()
        onClose()
        push({ type: 'admin' })
      } else {
        toast.error('Неверный аварийный ключ доступа!')
      }
    } catch {
      toast.error('Ошибка аварийного входа. Проверьте ключ!')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-md bg-card/95 border border-rose-500/20 rounded-3xl p-6 md:p-8 shadow-2xl relative overflow-hidden"
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-muted-foreground hover:text-foreground rounded-full hover:bg-muted/50 transition-colors"
        >
          <X className="size-5" />
        </button>

        {tab === 'user' ? (
          <>
            <div className="flex flex-col items-center text-center mb-6">
              <div className="p-3 bg-rose-500/10 rounded-2xl border border-rose-500/20 text-rose-400 mb-3">
                <User className="size-8" />
              </div>
              <h2 className="text-xl md:text-2xl font-black tracking-tight text-foreground font-heading">
                Профиль Игрока BlackRose
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                Введите ваш никнейм в игре для подачи заявок в гильдии и сохранения локальных
                настроек
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider block mb-1.5">
                  Игровой Никнейм (Slayer Name)
                </label>
                <Input
                  type="text"
                  placeholder="Например: Bannibal"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSaveProfile()}
                  className="h-12 rounded-xl border-rose-500/20 bg-background/50 font-bold"
                />
              </div>

              <Button
                onClick={handleSaveProfile}
                disabled={isSubmitting}
                className="w-full h-12 rounded-xl rose-glow-btn font-bold text-sm"
              >
                <Sparkles className="size-4 mr-2" />
                Сохранить Профиль
              </Button>

              <div className="relative my-4">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border/40" />
                </div>
                <div className="relative flex justify-center text-[10px] uppercase">
                  <span className="bg-card px-2 text-muted-foreground font-bold">Или</span>
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  haptic.light()
                  setTab('emergency')
                }}
                className="w-full py-2 text-xs font-bold text-muted-foreground hover:text-rose-400 transition-colors flex items-center justify-center gap-1.5"
              >
                <Shield className="size-3.5" />
                Аварийный Вход Администрации
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="flex flex-col items-center text-center mb-6">
              <div className="p-3 bg-amber-500/10 rounded-2xl border border-amber-500/20 text-amber-400 mb-3">
                <KeyRound className="size-8" />
              </div>
              <h2 className="text-xl md:text-2xl font-black tracking-tight text-foreground font-heading">
                Аварийный Вход
              </h2>
              <p className="text-xs text-muted-foreground mt-1">
                Вход по криптографическому мастер-ключа разработчика (Emergency Master Key)
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider block mb-1.5">
                  Мастер-Ключ Разработчика
                </label>
                <Input
                  type="password"
                  placeholder="••••••••••••••••"
                  value={emergencyKey}
                  onChange={(e) => setEmergencyKey(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleEmergencyLogin()}
                  className="h-12 rounded-xl border-amber-500/20 bg-background/50 font-bold"
                />
              </div>

              <Button
                onClick={handleEmergencyLogin}
                disabled={isSubmitting}
                className="w-full h-12 rounded-xl bg-amber-600 hover:bg-amber-500 font-bold text-sm text-white"
              >
                <Shield className="size-4 mr-2" />
                Подтвердить Аварийный Вход
              </Button>

              <button
                type="button"
                onClick={() => {
                  haptic.light()
                  setTab('user')
                }}
                className="w-full py-2 text-xs font-bold text-muted-foreground hover:text-foreground transition-colors text-center"
              >
                « Назад к профилю игрока
              </button>
            </div>
          </>
        )}
      </motion.div>
    </div>
  )
}
