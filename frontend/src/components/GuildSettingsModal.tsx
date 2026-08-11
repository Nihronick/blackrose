import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, Shield, X } from 'lucide-react'
import type { FC } from 'react'
import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { apiUpdateGuildSettings } from '@/lib/api'
import { haptic } from '@/lib/haptic'

interface GuildSettingsModalProps {
  guild: {
    id: number
    name: string
    icon_url?: string | null
    description?: string | null
  }
  onClose: () => void
}

const PRESET_LOGOS = [
  {
    name: 'Черная Роза',
    url: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=300&q=80',
  },
  {
    name: 'Золотой Дракон',
    url: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?auto=format&fit=crop&w=300&q=80',
  },
  {
    name: 'Корона Мастера',
    url: 'https://images.unsplash.com/photo-1569982175971-d92b01cf8694?auto=format&fit=crop&w=300&q=80',
  },
  {
    name: 'Легендарные Клинки',
    url: 'https://images.unsplash.com/photo-1589241062272-c0a000072dfa?auto=format&fit=crop&w=300&q=80',
  },
  {
    name: 'Магическая Руна',
    url: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=300&q=80',
  },
  {
    name: 'Штормовой Щит',
    url: 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=300&q=80',
  },
]

export const GuildSettingsModal: FC<GuildSettingsModalProps> = ({ guild, onClose }) => {
  const queryClient = useQueryClient()
  const [name, setName] = useState(guild.name)
  const [iconUrl, setIconUrl] = useState(guild.icon_url || '')
  const [description, setDescription] = useState(guild.description || '')

  const updateMutation = useMutation({
    mutationFn: (data: { name: string; icon_url?: string; description?: string }) =>
      apiUpdateGuildSettings(guild.id, data),
    onSuccess: () => {
      haptic.success()
      toast.success('Настройки и логотип гильдии успешно сохранены!')
      queryClient.invalidateQueries({ queryKey: ['guild-roster', guild.id] })
      onClose()
    },
    onError: (err: any) => {
      haptic.error()
      toast.error(err?.response?.data?.detail || 'Ошибка сохранения настроек гильдии')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) {
      toast.error('Название гильдии не может быть пустым')
      return
    }
    updateMutation.mutate({
      name: name.trim(),
      icon_url: iconUrl.trim() || undefined,
      description: description.trim() || undefined,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-lg glass-card rounded-[28px] p-6 border border-rose-500/30 shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between pb-4 border-b border-border/10 mb-5">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
              <Shield className="size-6" />
            </div>
            <div>
              <h2 className="text-xl font-black font-heading uppercase tracking-tight">
                Настройки Гильдии
              </h2>
              <p className="text-xs text-muted-foreground">
                Редактор названия, логотипа и описания гильдии
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-muted-foreground hover:bg-muted/50 transition-colors"
          >
            <X className="size-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Logo Preview & Custom URL */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-2 block">
              Логотип Гильдии
            </label>
            <div className="flex items-center gap-4 mb-4">
              <div className="size-20 rounded-2xl bg-rose-500/10 border border-rose-500/30 overflow-hidden flex items-center justify-center shrink-0 shadow-inner">
                {iconUrl ? (
                  <img src={iconUrl} alt="Preview" className="size-full object-cover" />
                ) : (
                  <Shield className="size-8 text-rose-400" />
                )}
              </div>
              <div className="flex-1 space-y-2">
                <input
                  type="text"
                  placeholder="Вставьте URL изображения (https://...)"
                  value={iconUrl}
                  onChange={(e) => setIconUrl(e.target.value)}
                  className="w-full h-10 px-3 text-xs rounded-xl bg-background/50 border border-border/20 focus:border-rose-500 focus:outline-none transition-colors"
                />
                <p className="text-[10px] text-muted-foreground">
                  Выберите пресет ниже или укажите прямую ссылку на картинку
                </p>
              </div>
            </div>

            {/* Presets */}
            <div className="grid grid-cols-6 gap-2">
              {PRESET_LOGOS.map((preset) => (
                <button
                  key={preset.name}
                  type="button"
                  onClick={() => {
                    haptic.light()
                    setIconUrl(preset.url)
                  }}
                  className={`relative size-12 rounded-xl overflow-hidden border transition-all ${
                    iconUrl === preset.url
                      ? 'border-rose-500 ring-2 ring-rose-500/40 scale-105'
                      : 'border-border/20 hover:border-rose-500/40 opacity-70 hover:opacity-100'
                  }`}
                  title={preset.name}
                >
                  <img src={preset.url} alt={preset.name} className="size-full object-cover" />
                  {iconUrl === preset.url && (
                    <div className="absolute inset-0 bg-rose-500/30 flex items-center justify-center">
                      <Check className="size-4 text-white drop-shadow-md" />
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Name */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1 block">
              Название Гильдии
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full h-11 px-4 text-sm font-bold rounded-xl bg-background/50 border border-border/20 focus:border-rose-500 focus:outline-none transition-colors"
              placeholder="Название гильдии"
            />
          </div>

          {/* Description */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-1 block">
              Описание Гильдии
            </label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-3 text-xs rounded-xl bg-background/50 border border-border/20 focus:border-rose-500 focus:outline-none transition-colors resize-none"
              placeholder="Короткое описание или девиз гильдии..."
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-border/10">
            <Button type="button" variant="ghost" onClick={onClose} className="h-10 text-xs">
              Отмена
            </Button>
            <Button
              type="submit"
              disabled={updateMutation.isPending}
              className="rose-glow-btn h-10 px-6 text-xs"
            >
              {updateMutation.isPending ? 'Сохранение...' : 'Сохранить логотип и настройки'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
