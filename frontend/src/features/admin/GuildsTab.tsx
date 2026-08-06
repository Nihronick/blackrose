import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  apiGuilds,
  apiAdminCreateGuild,
  apiAdminDeleteGuild,
  apiGuildRequests,
  apiApproveGuildRequest,
  apiRejectGuildRequest,
  apiUpdateGuildMember,
  apiRemoveGuildMember,
  apiGuildRoster,
} from '@/lib/api'
import type { Guild, GuildJoinRequest, GuildMember } from '@/lib/types'
import { Shield, Plus, Check, X, Trash2, UserCheck, Settings, ShieldAlert } from 'lucide-react'
import { getRankIcon, getRankName } from '@/lib/rankIcons'

export const GuildsTab = () => {
  const queryClient = useQueryClient()
  const [selectedGuildId, setSelectedGuildId] = useState<number | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newGuildName, setNewGuildName] = useState('')
  const [newGuildDesc, setNewGuildDesc] = useState('')
  const [newGuildMax, setNewGuildMax] = useState(20)

  // Fetch all guilds
  const { data: guildsData, isLoading: loadingGuilds } = useQuery({
    queryKey: ['admin_guilds'],
    queryFn: apiGuilds,
  })

  const guilds = guildsData?.guilds ?? []

  // Fetch pending requests for selected guild or first guild
  const currentGuildId = selectedGuildId ?? (guilds[0]?.id ?? null)

  const { data: requestsData } = useQuery({
    queryKey: ['admin_guild_requests', currentGuildId],
    queryFn: () => (currentGuildId ? apiGuildRequests(currentGuildId) : Promise.resolve({ requests: [] })),
    enabled: !!currentGuildId,
  })

  const { data: rosterData } = useQuery({
    queryKey: ['admin_guild_roster', currentGuildId],
    queryFn: () => (currentGuildId ? apiGuildRoster(currentGuildId) : Promise.resolve(null)),
    enabled: !!currentGuildId,
  })

  // Create Guild Mutation
  const createGuildMutation = useMutation({
    mutationFn: () =>
      apiAdminCreateGuild({
        name: newGuildName,
        description: newGuildDesc,
        max_members: newGuildMax,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin_guilds'] })
      setShowCreateModal(false)
      setNewGuildName('')
      setNewGuildDesc('')
    },
  })

  // Delete Guild Mutation
  const deleteGuildMutation = useMutation({
    mutationFn: (id: number) => apiAdminDeleteGuild(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin_guilds'] })
    },
  })

  // Approve Request Mutation
  const approveMutation = useMutation({
    mutationFn: (reqId: number) => apiApproveGuildRequest(reqId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin_guild_requests', currentGuildId] })
      queryClient.invalidateQueries({ queryKey: ['admin_guild_roster', currentGuildId] })
      queryClient.invalidateQueries({ queryKey: ['admin_guilds'] })
    },
  })

  // Reject Request Mutation
  const rejectMutation = useMutation({
    mutationFn: (reqId: number) => apiRejectGuildRequest(reqId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin_guild_requests', currentGuildId] })
    },
  })

  // Update Member Rank Mutation
  const updateMemberMutation = useMutation({
    mutationFn: ({ memberId, data }: { memberId: number; data: Record<string, unknown> }) =>
      apiUpdateGuildMember(memberId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin_guild_roster', currentGuildId] })
    },
  })

  // Remove Member Mutation
  const removeMemberMutation = useMutation({
    mutationFn: (memberId: number) => apiRemoveGuildMember(memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin_guild_roster', currentGuildId] })
      queryClient.invalidateQueries({ queryKey: ['admin_guilds'] })
    },
  })

  const requests = requestsData?.requests ?? []
  const members = rosterData?.members ?? []

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary" /> Управление гильдиями
          </h2>
          <p className="text-sm text-muted-foreground">
            Создание гильдий, подтверждение заявок, управление рангами и составом.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-all text-sm"
        >
          <Plus className="w-4 h-4" /> Создать гильдию
        </button>
      </div>

      {/* Guild Selector */}
      {loadingGuilds ? (
        <div className="h-16 skeleton rounded-2xl" />
      ) : guilds.length === 0 ? (
        <div className="text-center py-10 border border-dashed rounded-2xl text-muted-foreground">
          Гильдий пока нет. Создайте первую гильдию!
        </div>
      ) : (
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none">
          {guilds.map((g) => {
            const isSelected = g.id === currentGuildId
            return (
              <button
                key={g.id}
                onClick={() => setSelectedGuildId(g.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all whitespace-nowrap ${
                  isSelected
                    ? 'border-primary bg-primary/10 text-primary shadow-sm'
                    : 'border-border/40 hover:bg-accent/50 text-muted-foreground'
                }`}
              >
                <Shield className="w-4 h-4" />
                {g.name}
                <span className="text-xs px-2 py-0.5 rounded-full bg-background/50 border border-border/20">
                  {g.member_count}/{g.max_members}
                </span>
              </button>
            )
          })}
        </div>
      )}

      {currentGuildId && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Pending Requests Section */}
          <div className="lg:col-span-1 space-y-4">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-amber-500" /> Заявки на вступление ({requests.length})
            </h3>
            {requests.length === 0 ? (
              <div className="text-sm text-muted-foreground p-4 text-center border border-border/20 rounded-xl bg-card/30">
                Нет активных заявок
              </div>
            ) : (
              <div className="space-y-3">
                {requests.map((req) => (
                  <div
                    key={req.id}
                    className="p-4 rounded-xl border border-amber-500/20 bg-amber-500/5 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm">{req.nickname}</span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(req.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {req.message && (
                      <p className="text-xs text-muted-foreground italic bg-background/50 p-2 rounded-lg">
                        "{req.message}"
                      </p>
                    )}
                    <div className="flex gap-2 pt-1">
                      <button
                        onClick={() => approveMutation.mutate(req.id)}
                        disabled={approveMutation.isPending}
                        className="flex-1 flex items-center justify-center gap-1 text-xs py-1.5 rounded-lg bg-emerald-500 text-white font-medium hover:bg-emerald-600 transition-colors"
                      >
                        <Check className="w-3.5 h-3.5" /> Принять
                      </button>
                      <button
                        onClick={() => rejectMutation.mutate(req.id)}
                        disabled={rejectMutation.isPending}
                        className="flex-1 flex items-center justify-center gap-1 text-xs py-1.5 rounded-lg bg-destructive/10 text-destructive font-medium hover:bg-destructive/20 transition-colors"
                      >
                        <X className="w-3.5 h-3.5" /> Отклонить
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Guild Members Roster Management */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold flex items-center gap-2">
                <Settings className="w-4 h-4 text-primary" /> Состав гильдии ({members.length})
              </h3>
              {currentGuildId && (
                <button
                  onClick={() => {
                    if (confirm('Вы уверены, что хотите удалить эту гильдию?')) {
                      deleteGuildMutation.mutate(currentGuildId)
                    }
                  }}
                  className="text-xs text-destructive hover:underline flex items-center gap-1"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Удалить гильдию
                </button>
              )}
            </div>

            <div className="border border-border/40 rounded-xl overflow-hidden bg-card/30">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-muted/40 uppercase text-muted-foreground font-semibold border-b border-border/30">
                    <tr>
                      <th className="p-3">Никнейм</th>
                      <th className="p-3">Ранг</th>
                      <th className="p-3">Стадия</th>
                      <th className="p-3">Роль</th>
                      <th className="p-3">Статус</th>
                      <th className="p-3 text-right">Действия</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/20">
                    {members.map((m) => {
                      const icon = getRankIcon(m.rank)
                      return (
                        <tr key={m.id} className="hover:bg-accent/30 transition-colors">
                          <td className="p-3 font-medium">{m.nickname}</td>
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              {icon && <img src={icon} alt="" className="w-5 h-5 object-contain" />}
                              <select
                                value={m.rank}
                                onChange={(e) =>
                                  updateMemberMutation.mutate({
                                    memberId: m.id,
                                    data: { rank: Number(e.target.value), rank_confirmed: true },
                                  })
                                }
                                className="bg-background border border-border/40 rounded px-1.5 py-0.5 text-xs"
                              >
                                {Array.from({ length: 21 }, (_, i) => i + 1).map((r) => (
                                  <option key={r} value={r}>
                                    {r} - {getRankName(r)}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </td>
                          <td className="p-3">{m.stage}</td>
                          <td className="p-3">
                            <select
                              value={m.guild_role}
                              onChange={(e) =>
                                updateMemberMutation.mutate({
                                  memberId: m.id,
                                  data: { guild_role: e.target.value },
                                })
                              }
                              className="bg-background border border-border/40 rounded px-1.5 py-0.5 text-xs"
                            >
                              <option value="guild_member">Участник</option>
                              <option value="guild_vice_master">Вице-мастер</option>
                              <option value="guild_master">Мастер</option>
                            </select>
                          </td>
                          <td className="p-3">
                            <select
                              value={m.status}
                              onChange={(e) =>
                                updateMemberMutation.mutate({
                                  memberId: m.id,
                                  data: { status: e.target.value },
                                })
                              }
                              className="bg-background border border-border/40 rounded px-1.5 py-0.5 text-xs"
                            >
                              <option value="active">Активен</option>
                              <option value="trial">Присмотр</option>
                              <option value="left">Выбыл</option>
                              <option value="reserve">Заранее</option>
                            </select>
                          </td>
                          <td className="p-3 text-right">
                            <button
                              onClick={() => {
                                if (confirm(`Удалить ${m.nickname} из гильдии?`)) {
                                  removeMemberMutation.mutate(m.id)
                                }
                              }}
                              className="p-1 rounded text-destructive hover:bg-destructive/10 transition-colors"
                              title="Удалить"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Guild Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-md bg-card border border-border/40 rounded-2xl p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold">Создать новую гильдию</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Название гильдии</label>
                <input
                  type="text"
                  value={newGuildName}
                  onChange={(e) => setNewGuildName(e.target.value)}
                  placeholder="Например: BlackRose Prime"
                  className="w-full px-3 py-2 rounded-xl border border-border/40 bg-background text-foreground"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Описание</label>
                <textarea
                  value={newGuildDesc}
                  onChange={(e) => setNewGuildDesc(e.target.value)}
                  placeholder="Описание или девиз гильдии..."
                  rows={3}
                  className="w-full px-3 py-2 rounded-xl border border-border/40 bg-background text-foreground"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1">Макс. участников</label>
                <input
                  type="number"
                  value={newGuildMax}
                  onChange={(e) => setNewGuildMax(Number(e.target.value))}
                  min={1}
                  max={50}
                  className="w-full px-3 py-2 rounded-xl border border-border/40 bg-background text-foreground"
                />
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 py-2 rounded-xl border border-border/40 hover:bg-accent transition-colors text-sm font-medium"
              >
                Отмена
              </button>
              <button
                onClick={() => createGuildMutation.mutate()}
                disabled={!newGuildName.trim() || createGuildMutation.isPending}
                className="flex-1 py-2 rounded-xl bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity text-sm disabled:opacity-50"
              >
                Создать
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
