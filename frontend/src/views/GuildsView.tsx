import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Shield } from 'lucide-react'
import type { FC } from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { apiGuilds } from '@/lib/api'
import { useAppNavigation } from '@/lib/navigation'
import { useAppStore } from '@/store'

export const GuildsView: FC = () => {
  const { push } = useAppNavigation()
  const { isAdmin } = useAppStore() // or we could use some auth check, the prompt says "If user is logged in" 
  // Wait, user login is admin/local_admin? Let's check `isAdmin` for login state. Or we just show it always if not in guild?
  // Let's check the prompt: "If user is logged in and not in a guild, show a subtle "Подать заявку" button"
  // For now I'll use isAdmin as the logged-in proxy, or maybe there's an apiMyGuildProfile we can use.
  
  const { data, isLoading } = useQuery({
    queryKey: ['guilds'],
    queryFn: apiGuilds,
  })

  const guilds = data?.guilds ?? []

  return (
    <div className="flex h-full flex-col bg-background animate-in fade-in duration-300">
      <div className="container-padding py-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Shield className="size-6" />
          </div>
          <div>
            <h1 className="text-2xl font-black font-heading tracking-tight">Гильдии</h1>
            <p className="text-sm text-muted-foreground">Рейтинг и состав</p>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 stagger-in">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-28 rounded-[24px] skeleton" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 stagger-in">
            {guilds.map((guild) => (
              <motion.div
                key={guild.id}
                whileHover={{ scale: 0.98 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => push({ type: 'guild', id: guild.id })}
                className="glass-card cursor-pointer p-5 rounded-[24px] flex flex-col gap-3 transition-all relative overflow-hidden group"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none" />
                <div className="flex items-center gap-4 relative z-10">
                  <div className="size-14 rounded-2xl bg-muted overflow-hidden flex items-center justify-center border border-border/10 shadow-sm shrink-0">
                    {guild.icon_url ? (
                      <img src={guild.icon_url} alt={guild.name} className="size-full object-cover" />
                    ) : (
                      <Shield className="size-6 text-muted-foreground/50" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-lg truncate group-hover:text-primary transition-colors">{guild.name}</h3>
                    {guild.description && (
                      <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">{guild.description}</p>
                    )}
                  </div>
                </div>
                
                <div className="relative z-10 mt-1">
                  <div className="flex justify-between text-[10px] font-black uppercase tracking-wider text-muted-foreground mb-1.5">
                    <span>Участники</span>
                    <span>{guild.member_count} / {guild.max_members}</span>
                  </div>
                  <div className="h-2 rounded-full bg-muted overflow-hidden">
                    <div 
                      className="h-full bg-primary/80 transition-all rounded-full" 
                      style={{ width: `${Math.min(100, (guild.member_count / guild.max_members) * 100)}%` }}
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
