import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Edit2, Shield, Target, Trophy, UserPlus, Users } from 'lucide-react'
import type { FC } from 'react'
import { useState } from 'react'
import { useParams } from 'react-router-dom'

import { GuildJoinModal } from '@/components/GuildJoinModal'
import { GuildProfileModal } from '@/components/GuildProfileModal'
import { Button } from '@/components/ui/button'
import { apiGuildRoster, apiMyGuildProfile } from '@/lib/api'
import { getRankIcon, getRankName } from '@/lib/rankIcons'

interface GuildRosterViewProps {
  guildId: number
}

export const GuildRosterView: FC<GuildRosterViewProps> = ({ guildId }) => {
  const [profileModalOpen, setProfileModalOpen] = useState(false)
  const [joinModalOpen, setJoinModalOpen] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['guild-roster', guildId],
    queryFn: () => apiGuildRoster(guildId),
    enabled: !Number.isNaN(guildId) && guildId > 0,
  })

  const { data: myProfileData } = useQuery({
    queryKey: ['my-guild-profile'],
    queryFn: apiMyGuildProfile,
  })

  const roster = data?.members ?? []
  const stats = data?.stats
  const guild = data?.guild
  const myProfile = myProfileData?.profile

  const isMyGuild = myProfile?.guild_id === guildId
  const canJoin = !myProfile

  // Row color logic
  const getRowClass = (status: string) => {
    switch (status) {
      case 'trial':
        return 'bg-amber-500/10 hover:bg-amber-500/20'
      case 'left':
        return 'bg-red-500/10 hover:bg-red-500/20 opacity-75'
      case 'reserve':
        return 'bg-blue-500/10 hover:bg-blue-500/20'
      default:
        return 'hover:bg-muted/50'
    }
  }

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'guild_master':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-500 border border-amber-500/20">
            Мастер
          </span>
        )
      case 'guild_vice_master':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-300/20 text-slate-300 border border-slate-300/20">
            Вице-мастер
          </span>
        )
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-muted text-muted-foreground border border-border/10">
            Участник
          </span>
        )
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'trial':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-500">
            Испытательный
          </span>
        )
      case 'left':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/10 text-red-500">
            Покинул
          </span>
        )
      case 'reserve':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-500">
            Резерв
          </span>
        )
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-green-500/10 text-green-500">
            Актив
          </span>
        )
    }
  }

  return (
    <div className="flex flex-col min-h-full pb-20 rose-mesh-bg">
      {/* Header */}
      <div className="relative pt-8 pb-6 px-4 md:px-8 border-b border-rose-500/20 overflow-hidden bg-gradient-to-r from-rose-950/40 via-card/70 to-card/90">
        <div className="flex flex-col gap-6 relative z-10">
          <div className="flex items-center gap-4">
            <div className="size-16 md:size-20 rounded-3xl bg-rose-500/10 shadow-xl border border-rose-500/30 overflow-hidden flex items-center justify-center shrink-0">
              {guild?.icon_url ? (
                <img src={guild.icon_url} alt={guild.name} className="size-full object-cover" />
              ) : (
                <Shield className="size-8 text-rose-400" />
              )}
            </div>
            <div>
              <h1 className="text-3xl font-black font-heading tracking-tight uppercase text-foreground">
                {guild?.name || 'Клановый Состав'}
              </h1>
              <p className="text-xs text-muted-foreground font-medium mt-1">
                {guild?.description || 'Официальный ростер участников гильдии Slayer Legend'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {isMyGuild && (
              <Button
                size="sm"
                variant="secondary"
                className="rose-glow-btn h-10 px-5 text-xs"
                onClick={() => setProfileModalOpen(true)}
              >
                <Edit2 className="size-4 mr-2" />
                Мой профиль
              </Button>
            )}
            {canJoin && (
              <Button
                size="sm"
                className="rose-glow-btn h-10 px-5 text-xs"
                onClick={() => setJoinModalOpen(true)}
              >
                <UserPlus className="size-4 mr-2" />
                Подать заявку
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="p-4 md:p-8">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 md:gap-6 mb-8 stagger-in">
          <div className="glass-card rounded-2xl p-4 md:p-5 relative overflow-hidden group">
            <div className="absolute top-2 right-2 p-2 bg-primary/10 rounded-xl">
              <Users className="size-4 md:size-5 text-primary" />
            </div>
            <div className="text-2xl md:text-3xl font-black mt-2 md:mt-4">
              {stats?.member_count || 0}
            </div>
            <div className="text-[10px] md:text-xs font-bold uppercase tracking-wider text-muted-foreground mt-1">
              Участников
            </div>
          </div>
          <div className="glass-card rounded-2xl p-4 md:p-5 relative overflow-hidden group">
            <div className="absolute top-2 right-2 p-2 bg-amber-500/10 rounded-xl">
              <Trophy className="size-4 md:size-5 text-amber-500" />
            </div>
            <div className="text-2xl md:text-3xl font-black mt-2 md:mt-4 text-amber-500">
              {stats?.total_ranks || 0}
            </div>
            <div className="text-[10px] md:text-xs font-bold uppercase tracking-wider text-muted-foreground mt-1">
              Сумма рангов
            </div>
          </div>
          <div className="glass-card rounded-2xl p-4 md:p-5 relative overflow-hidden group">
            <div className="absolute top-2 right-2 p-2 bg-blue-500/10 rounded-xl">
              <Target className="size-4 md:size-5 text-blue-500" />
            </div>
            <div className="text-2xl md:text-3xl font-black mt-2 md:mt-4 text-blue-500">
              {(stats?.average_rank || 0).toFixed(1)}
            </div>
            <div className="text-[10px] md:text-xs font-bold uppercase tracking-wider text-muted-foreground mt-1">
              Средний ранг
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="glass-card rounded-[24px] overflow-hidden">
          {isLoading ? (
            <div className="p-6 text-center text-muted-foreground">Загрузка состава...</div>
          ) : roster.length === 0 ? (
            <div className="p-6 text-center text-muted-foreground">
              В гильдии пока нет участников.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="bg-muted/30 text-[10px] uppercase tracking-wider font-bold text-muted-foreground">
                  <tr>
                    <th className="px-6 py-4 rounded-tl-[24px]">#</th>
                    <th className="px-6 py-4">Участник</th>
                    <th className="px-6 py-4">Ранг</th>
                    <th className="px-6 py-4">Стадия</th>
                    <th className="px-6 py-4">Роль</th>
                    <th className="px-6 py-4 rounded-tr-[24px]">Статус</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/10">
                  {roster.map((member, index) => (
                    <tr
                      key={member.id}
                      className={`transition-colors ${getRowClass(member.status)}`}
                    >
                      <td className="px-6 py-4 font-medium text-muted-foreground">{index + 1}</td>
                      <td className="px-6 py-4 font-bold">{member.nickname}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <img
                            src={getRankIcon(member.rank)}
                            alt={getRankName(member.rank)}
                            loading="lazy"
                            decoding="async"
                            className="size-6 object-contain drop-shadow-md"
                          />
                          <span className="font-black bg-background/50 px-2 py-0.5 rounded-lg border border-border/10 shadow-sm">
                            {member.rank}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium">{member.stage || '-'}</td>
                      <td className="px-6 py-4">{getRoleBadge(member.guild_role)}</td>
                      <td className="px-6 py-4">{getStatusBadge(member.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {profileModalOpen && myProfile && (
        <GuildProfileModal profile={myProfile} onClose={() => setProfileModalOpen(false)} />
      )}

      {joinModalOpen && guild && (
        <GuildJoinModal guild={guild} onClose={() => setJoinModalOpen(false)} />
      )}
    </div>
  )
}
