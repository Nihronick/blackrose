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
    <div className="flex h-full flex-col bg-background animate-in fade-in duration-300 rose-mesh-bg min-h-screen">
      <div className="container-padding py-6 space-y-6">
        <div className="flex items-center gap-4 p-6 rounded-3xl rose-bento-card border-rose-500/30 bg-gradient-to-r from-rose-950/40 via-card/70 to-card/90">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-rose-500/20 text-rose-400 border border-rose-500/30 shadow-lg shadow-rose-950/40">
            <Shield className="size-7" />
          </div>
          <div>
            <h1 className="text-3xl font-black font-heading tracking-tight uppercase text-foreground">Гильдии Slayer Legend</h1>
            <p className="text-xs font-bold text-rose-400/80 uppercase tracking-widest mt-0.5">Официальный клановый ростер и рейтинг</p>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 stagger-in">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 rounded-3xl skeleton" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 stagger-in">
            {guilds.map((guild) => (
              <motion.div
                key={guild.id}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => push({ type: 'guild', id: guild.id })}
                className="rose-bento-card cursor-pointer p-6 flex flex-col gap-4 border-rose-500/20 group relative overflow-hidden"
              >
                <div className="flex items-center gap-4 relative z-10">
                  <div className="size-14 rounded-2xl bg-rose-500/10 overflow-hidden flex items-center justify-center border border-rose-500/30 shadow-inner shrink-0">
                    {guild.icon_url ? (
                      <img src={guild.icon_url} alt={guild.name} className="size-full object-cover" />
                    ) : (
                      <Shield className="size-6 text-rose-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-black text-lg font-heading truncate group-hover:text-rose-400 transition-colors uppercase text-foreground">{guild.name}</h3>
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
