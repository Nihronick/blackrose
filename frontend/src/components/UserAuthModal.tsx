import { haptic } from '@/lib/haptic'
import { motion } from 'framer-motion'
import { Shield, Sparkles, User, X } from 'lucide-react'
import { type FC, useState } from 'react'
import { toast } from 'sonner'
import { AdminLoginModal } from './AdminLoginModal'
import { Button } from './ui/button'
import { Input } from './ui/input'

interface UserAuthModalProps {
  onClose: () => void
  onSuccess?: () => void
}

export const UserAuthModal: FC<UserAuthModalProps> = ({ onClose, onSuccess }) => {
  const [mode, setMode] = useState<'user' | 'admin'>('user')
  const [nickname, setNickname] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  if (mode === 'admin') {
    return (
      <AdminLoginModal
        onSuccess={() => {
          onSuccess?.()
          onClose()
        }}
        onClose={onClose}
      />
    )
  }

  const handleSaveProfile = () => {
    const trimmed = nickname.trim()
    if (!trimmed) {
      toast.error('Введите ваш никнейм в игре!')
      return
    }
    haptic.medium()
    setIsSaving(true)

    // Save to localStorage as player session
    localStorage.setItem('slayer_nickname', trimmed)

    toast.success(`С возвращением, ${trimmed}!`)
    setIsSaving(false)
    onSuccess?.()
    onClose()
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

        <div className="flex flex-col items-center text-center mb-6">
          <div className="p-3 bg-rose-500/10 rounded-2xl border border-rose-500/20 text-rose-400 mb-3">
            <User className="size-8" />
          </div>
          <h2 className="text-xl md:text-2xl font-black tracking-tight text-foreground font-heading">
            Профиль Игрока BlackRose
          </h2>
          <p className="text-xs text-muted-foreground mt-1">
            Введите ваш никнейм в игре для подачи заявок в гильдии, сохранения билдов и написания
            отзывов
          </p>
        </div>

        {/* Form */}
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
            disabled={isSaving}
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
              setMode('admin')
            }}
            className="w-full py-2 text-xs font-bold text-muted-foreground hover:text-rose-400 transition-colors flex items-center justify-center gap-1.5"
          >
            <Shield className="size-3.5" />
            Панель Администрации (Admin Access)
          </button>
        </div>
      </motion.div>
    </div>
  )
}
