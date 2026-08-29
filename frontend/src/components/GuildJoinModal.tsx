import { useMutation } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'framer-motion'
import { Send, X } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiJoinGuild } from '@/lib/api'
import type { Guild } from '@/lib/types'

export const GuildJoinModal = ({ guild, onClose }: { guild: Guild; onClose: () => void }) => {
  const [nickname, setNickname] = useState('')
  const [message, setMessage] = useState('')

  const mutation = useMutation({
    mutationFn: apiJoinGuild,
    onSuccess: () => {
      toast.success('Заявка успешно отправлена!')
      onClose()
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Ошибка при отправке заявки')
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
              <h2 className="text-xl font-black font-heading">Вступление в гильдию</h2>
              <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full size-8">
                <X className="size-4" />
              </Button>
            </div>

            <div className="mb-6 p-4 rounded-2xl bg-primary/5 border border-primary/10">
              <div className="text-sm font-medium text-muted-foreground">Вы подаете заявку в</div>
              <div className="font-black text-lg text-primary mt-1">{guild.name}</div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground ml-1">
                  Игровой никнейм *
                </label>
                <Input
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  placeholder="Введите ваш ник в игре"
                  className="rounded-xl h-12 bg-muted/50 border-border/10 focus-visible:ring-primary/20"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider text-muted-foreground ml-1">
                  Сообщение (необязательно)
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Пара слов о себе..."
                  className="w-full rounded-xl p-3 bg-muted/50 border border-border/10 focus:outline-none focus:ring-2 focus:ring-primary/20 resize-none h-24 text-sm"
                />
              </div>
            </div>

            <Button
              className="w-full mt-6 h-12 rounded-xl font-bold bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={() => mutation.mutate({ guild_id: guild.id, nickname, message })}
              disabled={mutation.isPending || !nickname.trim()}
            >
              {mutation.isPending ? (
                'Отправка...'
              ) : (
                <>
                  <Send className="size-4 mr-2" />
                  Отправить заявку
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
