import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  type AdminUserItem,
  apiGetAdminUsers,
  apiToggleUserStatus,
  apiUpdateUserRole,
} from '@/lib/api'
import {
  Lock,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Unlock,
  User,
  Users,
} from '@/lib/icons'
import { type FC, useEffect, useState } from 'react'

const ROLES = [
  {
    key: 'project_admin',
    label: 'Владелец (Project Admin)',
    color: 'text-amber-400 bg-amber-500/20 border-amber-500/30',
  },
  {
    key: 'admin',
    label: 'Администратор (Admin)',
    color: 'text-violet-400 bg-violet-500/20 border-violet-500/30',
  },
  {
    key: 'editor',
    label: 'Редактор (Editor)',
    color: 'text-blue-400 bg-blue-500/20 border-blue-500/30',
  },
  {
    key: 'moderator',
    label: 'Модератор (Moderator)',
    color: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
  },
  {
    key: 'member',
    label: 'Участник (Member)',
    color: 'text-muted-foreground bg-muted border-white/10',
  },
]

export const UsersTab: FC = () => {
  const [users, setUsers] = useState<AdminUserItem[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState<number | null>(null)

  const loadUsers = async () => {
    setLoading(true)
    try {
      const data = await apiGetAdminUsers(search)
      setUsers(data.users || [])
      setTotalCount(data.total || 0)
    } catch (err) {
      console.error('Failed to load admin users:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      loadUsers()
    }, 300)
    return () => clearTimeout(timer)
  }, [search])

  const handleRoleChange = async (userId: number, newRole: string) => {
    setUpdatingId(userId)
    try {
      await apiUpdateUserRole(userId, newRole)
      setUsers((prev) => prev.map((u) => (u.user_id === userId ? { ...u, role: newRole } : u)))
    } catch (e: unknown) {
      alert('Ошибка при изменении роли: ' + ((e as Error).message || e))
    } finally {
      setUpdatingId(null)
    }
  }

  const handleToggleStatus = async (userId: number, currentStatus: boolean) => {
    setUpdatingId(userId)
    const nextStatus = !currentStatus
    try {
      await apiToggleUserStatus(userId, nextStatus)
      setUsers((prev) =>
        prev.map((u) => (u.user_id === userId ? { ...u, is_active: nextStatus } : u))
      )
    } catch (e: unknown) {
      alert('Ошибка изменения статуса пользователя: ' + ((e as Error).message || e))
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <div className="w-full space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 bg-gradient-to-r from-violet-950/40 via-card/60 to-indigo-950/40 backdrop-blur-xl border border-primary/20 rounded-3xl shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-2xl text-white shadow-lg shadow-violet-500/25 border border-white/10">
            <Users className="size-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black tracking-tight uppercase font-heading text-foreground">
              Управление Пользователями и Ролями (RBAC Manager)
            </h2>
            <p className="text-xs font-bold text-primary/80 uppercase tracking-widest mt-0.5">
              Дистанционный доступ, назначение прав и блокировка аккаунтов
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 bg-background/60 rounded-2xl border border-white/10 backdrop-blur-md">
            <span className="text-xs font-black uppercase tracking-wider text-foreground">
              Всего пользователей: <strong className="text-primary font-mono">{totalCount}</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Main Table Card */}
      <Card className="p-6 border border-primary/20 bg-gradient-to-br from-card/90 via-card/50 to-card/90 backdrop-blur-xl rounded-3xl space-y-6 shadow-2xl">
        {/* Search Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="relative w-full sm:w-96">
            <Search className="absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Поиск по имени или Telegram username..."
              className="h-11 rounded-2xl bg-background/80 border border-white/10 pl-11 text-xs text-foreground focus-visible:ring-primary/40 focus-visible:border-primary/50"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <Button
            variant="outline"
            size="sm"
            className="h-11 px-5 rounded-2xl font-bold text-xs uppercase tracking-wider gap-2 border-white/10 hover:bg-white/5"
            onClick={loadUsers}
            disabled={loading}
          >
            <RefreshCw className={`size-4 ${loading ? 'animate-spin' : ''}`} /> Обновить
          </Button>
        </div>

        {/* Users Table */}
        {users.length === 0 ? (
          <div className="p-12 text-center bg-background/30 rounded-3xl border border-dashed border-white/10 space-y-3">
            <User className="size-10 text-primary/40 mx-auto" />
            <p className="text-sm font-bold text-foreground">Пользователи не найдены</p>
            <p className="text-xs text-muted-foreground">Попробуйте изменить поисковый запрос</p>
          </div>
        ) : (
          <div className="divide-y divide-white/10 rounded-2xl border border-white/10 overflow-hidden bg-background/50 backdrop-blur-md">
            {users.map((u) => {
              const roleMeta = ROLES.find((r) => r.key === u.role) || ROLES[4]
              return (
                <div
                  key={u.user_id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-4 hover:bg-white/5 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="size-12 rounded-2xl bg-gradient-to-tr from-violet-600/30 to-indigo-600/30 border border-white/10 flex items-center justify-center text-primary font-black font-mono text-sm shrink-0">
                      #{u.user_id.toString().slice(-4)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-foreground text-sm">
                          {u.first_name || u.username || `User #${u.user_id}`}
                        </span>
                        {u.username && (
                          <span className="text-xs font-mono text-primary">@{u.username}</span>
                        )}
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase border ${
                            u.is_active
                              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                              : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                          }`}
                        >
                          {u.is_active ? 'Активен' : 'Заблокирован'}
                        </span>
                      </div>

                      <div className="text-[11px] text-muted-foreground mt-1 flex items-center gap-3">
                        <span>
                          ID: <code className="font-mono text-foreground">{u.user_id}</code>
                        </span>
                        {u.created_at && (
                          <span>
                            Регистрация: {new Date(u.created_at).toLocaleDateString('ru-RU')}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-center">
                    {/* Role Selector */}
                    <select
                      className={`h-10 rounded-xl px-3 text-xs font-black uppercase tracking-wider border cursor-pointer ${roleMeta.color}`}
                      value={u.role}
                      disabled={updatingId === u.user_id}
                      onChange={(e) => handleRoleChange(u.user_id, e.target.value)}
                    >
                      {ROLES.map((r) => (
                        <option key={r.key} value={r.key} className="bg-card text-foreground">
                          {r.label}
                        </option>
                      ))}
                    </select>

                    {/* Ban / Unban Toggle */}
                    <Button
                      variant={u.is_active ? 'destructive' : 'default'}
                      size="sm"
                      className={`h-10 px-4 rounded-xl text-xs font-bold gap-2 cursor-pointer ${
                        !u.is_active
                          ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                          : 'bg-rose-600/80 hover:bg-rose-600 text-white'
                      }`}
                      disabled={updatingId === u.user_id}
                      onClick={() => handleToggleStatus(u.user_id, u.is_active)}
                      title={u.is_active ? 'Заблокировать доступ' : 'Разблокировать доступ'}
                    >
                      {u.is_active ? (
                        <Lock className="size-3.5" />
                      ) : (
                        <Unlock className="size-3.5" />
                      )}
                      {u.is_active ? 'Заблокировать' : 'Разблокировать'}
                    </Button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </Card>
    </div>
  )
}
