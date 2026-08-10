import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'framer-motion'
import { AlertCircle, Save, X } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiUpdateMyGuildProfile } from '@/lib/api'
import { getRankIcon, getRankName } from '@/lib/rankIcons'
import type { GuildMember } from '@/lib/types'

export const GuildProfileModal = ({
  profile,
  onClose,
}: { profile: GuildMember; onClose: () => void }) => {
  const [nickname, setNickname] = useState(profile.nickname)
  const [stage, setStage] = useState(profile.stage.toString())

  const qc = useQueryClient()

  const mutation = useMutation({
    mutationFn: apiUpdateMyGuildProfile,
    onSuccess: () => {
      toast.success('Профиль успешно обновлен')
      qc.invalidateQueries({ queryKey: ['my-guild-profile'] })
      qc.invalidateQueries({ queryKey: ['guild-roster'] })
      onClose()
    },
    onError: (err: any) => {
      toast.error(err.message || 'Ошибка обновления профиля')
    },
  })

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-background/80 backdrop-blur-md"
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-md glass-card rounded-[32px] overflow-hidden shadow-2xl border border-border/20 z-10"
        >
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-black font-heading">Мой профиль</h2>
              <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full size-8">
                <X className="size-4" />
              </Button>
            </div>

            <div className="space-y-5">
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground ml-1">
                  Никнейм
                </label>
                <Input
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  className="rounded-xl h-12 bg-muted/50 border-border/10 focus-visible:ring-primary/20"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground ml-1">
                  Стадия
                </label>
                <Input
                  type="number"
                  value={stage}
                  onChange={(e) => setStage(e.target.value)}
                  className="rounded-xl h-12 bg-muted/50 border-border/10 focus-visible:ring-primary/20"
                />
              </div>

              <div className="p-4 rounded-2xl bg-muted/30 border border-border/10">
                <div className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-3">
                  Ранг
                </div>
                <div className="flex items-center gap-3">
                  <div className="size-12 rounded-xl bg-background shadow-sm border border-border/5 flex items-center justify-center">
                    <img
                      src={getRankIcon(profile.rank)}
                      className="size-8 object-contain"
                      alt="rank"
                    />
                  </div>
                  <div>
                    <div className="font-black text-lg">
                      {profile.rank} - {getRankName(profile.rank)}
                    </div>
                    {!profile.rank_confirmed && (
                      <div className="flex items-center text-xs text-amber-500 font-medium mt-0.5">
                        <AlertCircle className="size-3 mr-1" />
                        Требует подтверждения
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <Button
              className="w-full mt-6 h-12 rounded-xl font-bold bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={() => mutation.mutate({ nickname, stage: Number(stage) })}
              disabled={mutation.isPending}
            >
              {mutation.isPending ? (
                'Сохранение...'
              ) : (
                <>
                  <Save className="size-4 mr-2" />
                  Сохранить
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
