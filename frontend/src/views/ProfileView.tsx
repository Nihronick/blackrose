import { ErrorBoundary } from '@/components/ErrorBoundary'
import { Card, CardContent } from '@/components/ui/card'
import { useFavorites } from '@/hooks/useFavorites'
import { useHistory } from '@/hooks/useHistory'
import { useSheet } from '@/hooks/useSheet'
import { getStoredUser, clearStoredToken } from '@/lib/auth'
import { apiExportUserData, apiDeleteUserData } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import {
  BookOpen,
  ChevronRight,
  Download,
  FileText,
  Lock,
  LogOut,
  Moon,
  Settings,
  Shield,
  ShieldCheck,
  Star,
  Sun,
  Trash2,
  User as UserIcon,
} from '@/lib/icons'
import { useAppNavigation } from '@/lib/navigation'
import { useAppStore } from '@/store'
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'
import { motion, AnimatePresence } from 'framer-motion'
import { useState, type FC } from 'react'

export const ProfileView: FC = () => {
  const { history } = useHistory()
  const { favorites } = useFavorites()
  const { theme, setTheme, isAdmin, setIsAdmin } = useAppStore()
  const { push } = useAppNavigation()
  const sheet = useSheet()

  const tgUser =
    typeof window !== 'undefined'
      ? (
          window as unknown as {
            Telegram?: {
              WebApp?: {
                initDataUnsafe?: {
                  user?: {
                    first_name?: string
                    last_name?: string
                    username?: string
                    id?: number
                    photo_url?: string
                  }
                }
              }
            }
          }
        ).Telegram?.WebApp?.initDataUnsafe?.user
      : undefined

  const user = pipe(
    getStoredUser(),
    O.getOrElse(() => ({
      id: 0,
      first_name: 'Слеер',
      is_admin: false,
    }))
  )

  const stats = [
    { label: 'Прочитано', value: history.length, icon: BookOpen, color: 'text-primary' },
    { label: 'В закладках', value: favorites.length, icon: Star, color: 'text-amber-400' },
  ]

  const badges = [
    { id: 1, title: 'Новичок', desc: 'Первые шаги', icon: '🌱', active: true },
    { id: 2, title: 'Исследователь', desc: '5 гайдов', icon: '🔍', active: history.length >= 5 },
    { id: 3, title: 'Коллекционер', desc: '3 закладки', icon: '📚', active: favorites.length >= 3 },
  ]

  return (
    <div className="flex flex-col gap-6 animate-in fade-in zoom-in-95 duration-500 pb-8 stagger-in">
      {/* 1. Header with Avatar */}
      <section className="pt-4 container-padding">
        <div className="relative overflow-hidden rounded-[32px] mesh-bg p-6 border border-primary/15 shadow-2xl shadow-primary/10 ambient-glow texture-noise flex flex-col items-center text-center">
          <div className="absolute -right-10 -top-10 size-48 rounded-full bg-primary/20 blur-[80px] animate-pulse" />

          <div className="relative z-10 flex flex-col items-center">
            <div className="relative mb-4">
              <div className="size-24 rounded-full bg-background border-4 border-background shadow-xl overflow-hidden flex items-center justify-center p-1">
                <div className="size-full rounded-full bg-gradient-to-br from-primary/20 to-violet-500/20 flex items-center justify-center border border-primary/20">
                  {user.photo_url ? (
                    <img
                      src={user.photo_url}
                      alt=""
                      className="size-full object-cover rounded-full"
                    />
                  ) : (
                    <UserIcon className="size-10 text-primary" />
                  )}
                </div>
              </div>
              {isAdmin && (
                <div className="absolute -bottom-2 -right-2 size-8 rounded-full bg-rose-500 text-white flex items-center justify-center border-4 border-background shadow-lg">
                  <Shield className="size-4" />
                </div>
              )}
            </div>

            <h1 className="text-2xl font-black tracking-tight text-foreground font-heading">
              {tgUser?.first_name || user.first_name || 'Слеер'}{' '}
              {tgUser?.last_name || user.last_name || ''}
            </h1>
            <div className="flex items-center gap-2 mt-1">
              {tgUser?.username ? (
                <span className="text-xs font-medium text-muted-foreground/80">
                  @{tgUser.username}
                </span>
              ) : (
                <span className="text-xs font-medium text-muted-foreground/80">
                  ID: {tgUser?.id || user.id || 'Telegram User'}
                </span>
              )}
            </div>
            <div className="mt-3 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[11px] font-black uppercase tracking-wider flex items-center gap-1.5">
              <Shield className="size-3 text-rose-400" />
              <span>{isAdmin ? 'Project Lead / Admin' : 'Авторизованный Слеер (Telegram)'}</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Stats Grid */}
      <section className="container-padding">
        <div className="grid grid-cols-2 gap-4">
          {stats.map((stat, i) => {
            const Icon = stat.icon
            return (
              <Card key={i} className="card-elevated rounded-[24px] border border-border/10">
                <CardContent className="p-5 flex flex-col items-center text-center gap-2">
                  <div
                    className={`size-10 rounded-2xl bg-muted/50 flex items-center justify-center shadow-inner ${stat.color}`}
                  >
                    <Icon className="size-5" />
                  </div>
                  <div>
                    <div className="text-2xl font-black font-heading">{stat.value}</div>
                    <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground/60">
                      {stat.label}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>

      {/* 3. Achievements */}
      <section className="flex flex-col gap-4 mt-2">
        <div className="container-padding section-label font-heading">
          <Star className="size-3.5 text-amber-400" />
          <span>Достижения</span>
        </div>

        <div className="flex gap-4 overflow-x-auto scrollbar-premium px-5 sm:px-8 pb-4 no-scrollbar">
          {badges.map((badge) => (
            <div
              key={badge.id}
              className={`w-[140px] flex-shrink-0 flex flex-col items-center text-center gap-3 p-4 rounded-[24px] border transition-all ${
                badge.active
                  ? 'bg-muted/30 border-primary/20 shadow-glow'
                  : 'bg-muted/10 border-border/5 opacity-50 grayscale'
              }`}
            >
              <div className="text-4xl filter drop-shadow-md">{badge.icon}</div>
              <div>
                <h4 className="text-[13px] font-black font-heading leading-tight">{badge.title}</h4>
                <p className="text-[10px] text-muted-foreground/70 mt-1">{badge.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Settings */}
      <section className="container-padding flex flex-col gap-4 mt-2">
        <div className="section-label font-heading">
          <Settings className="size-3.5 text-muted-foreground" />
          <span>Настройки</span>
        </div>

        <div className="flex flex-col gap-3">
          <motion.button
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              haptic.light()
              setTheme(theme === 'light' ? 'dark' : 'light')
            }}
            className="flex items-center justify-between p-4 rounded-2xl bg-muted/20 border border-border/5 hover:bg-muted/30 transition-colors"
          >
            <div className="flex items-center gap-4">
              <div className="size-10 rounded-xl bg-background flex items-center justify-center shadow-sm">
                {theme === 'light' ? (
                  <Sun className="size-5 text-amber-500" />
                ) : (
                  <Moon className="size-5 text-primary" />
                )}
              </div>
              <div className="text-left">
                <h4 className="text-sm font-black font-heading">Тема оформления</h4>
                <p className="text-[11px] text-muted-foreground/60 font-medium">
                  {theme === 'light'
                    ? 'Светлая тема'
                    : theme === 'dark'
                      ? 'Темная тема'
                      : 'Системная тема'}
                </p>
              </div>
            </div>
            <div className="w-12 h-6 rounded-full bg-muted/50 relative border border-border/10">
              <div
                className={`absolute top-1/2 -translate-y-1/2 size-5 rounded-full bg-primary shadow-md transition-all duration-300 ${theme === 'dark' ? 'left-[26px]' : 'left-1'}`}
              />
            </div>
          </motion.button>

          {/* Admin Access Panel */}
          {isAdmin ? (
            <div className="flex flex-col gap-2 mt-2">
              <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  haptic.medium()
                  push({ type: 'admin' })
                }}
                className="flex items-center justify-between p-4 rounded-2xl bg-gradient-to-r from-primary/20 via-rose-500/10 to-primary/10 border border-primary/30 hover:border-primary/50 transition-all shadow-lg shadow-primary/10"
              >
                <div className="flex items-center gap-4">
                  <div className="size-10 rounded-xl bg-primary text-primary-foreground flex items-center justify-center shadow-md">
                    <ShieldCheck className="size-5" />
                  </div>
                  <div className="text-left">
                    <h4 className="text-sm font-black font-heading text-foreground flex items-center gap-2">
                      Панель Управления
                      <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary text-[10px] font-black uppercase">
                        Admin
                      </span>
                    </h4>
                    <p className="text-[11px] text-muted-foreground font-medium">
                      Управление гайдами, участниками и синхронизацией
                    </p>
                  </div>
                </div>
                <ChevronRight className="size-5 text-primary" />
              </motion.button>

              <motion.button
                whileTap={{ scale: 0.98 }}
                onClick={() => {
                  haptic.medium()
                  setIsAdmin(false)
                }}
                className="flex items-center justify-between p-3.5 rounded-2xl bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="size-8 rounded-lg bg-background flex items-center justify-center shadow-sm">
                    <LogOut className="size-4 text-rose-500" />
                  </div>
                  <div className="text-left">
                    <h4 className="text-xs font-bold font-heading text-rose-500">
                      Выйти из админки
                    </h4>
                  </div>
                </div>
                <ChevronRight className="size-4 text-rose-500/40" />
              </motion.button>
            </div>
          ) : (
            <motion.button
              whileTap={{ scale: 0.98 }}
              onClick={() => {
                haptic.medium()
                sheet.present({ type: 'login' })
              }}
              className="flex items-center justify-between p-4 rounded-2xl bg-muted/20 border border-border/10 hover:bg-muted/30 transition-colors mt-2"
            >
              <div className="flex items-center gap-4">
                <div className="size-10 rounded-xl bg-background flex items-center justify-center shadow-sm">
                  <Lock className="size-5 text-muted-foreground" />
                </div>
                <div className="text-left">
                  <h4 className="text-sm font-black font-heading text-foreground">
                    Вход администратора
                  </h4>
                  <p className="text-[11px] text-muted-foreground/60 font-medium">
                    Войти по паролю или аварийному ключу
                  </p>
                </div>
              </div>
              <ChevronRight className="size-5 text-muted-foreground/40" />
            </motion.button>
          )}

          {/* GDPR & 152-ФЗ Compliance Section */}
          <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-border/10">
            <h4 className="text-xs font-bold font-heading text-muted-foreground px-2 uppercase tracking-wider">
              Конфиденциальность и Данные (152-ФЗ / GDPR)
            </h4>

            <motion.button
              whileTap={{ scale: 0.98 }}
              onClick={async () => {
                haptic.medium()
                try {
                  const data = await apiExportUserData()
                  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `blackrose_user_data_${user.id || 'me'}.json`
                  a.click()
                  URL.revokeObjectURL(url)
                } catch {
                  alert('Для экспорта персональных данных требуется авторизация')
                }
              }}
              className="flex items-center justify-between p-3.5 rounded-2xl bg-muted/10 border border-border/10 hover:bg-muted/20 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="size-8 rounded-lg bg-background flex items-center justify-center shadow-sm">
                  <Download className="size-4 text-primary" />
                </div>
                <div className="text-left">
                  <h4 className="text-xs font-bold font-heading text-foreground">
                    Выгрузить мои данные (JSON)
                  </h4>
                  <p className="text-[10px] text-muted-foreground/60">
                    GDPR Art. 20 / 152-ФЗ ст. 14 — переносимость данных
                  </p>
                </div>
              </div>
              <ChevronRight className="size-4 text-muted-foreground/40" />
            </motion.button>

            <motion.button
              whileTap={{ scale: 0.98 }}
              onClick={async () => {
                haptic.heavy()
                if (window.confirm('Вы уверены, что хотите удалить все свои данные (закладки, реакции, историю)? Это действие необратимо.')) {
                  try {
                    await apiDeleteUserData()
                    clearStoredToken()
                    alert('Все ваши персональные данные успешно удалены.')
                    window.location.reload()
                  } catch {
                    alert('Для удаления данных требуется авторизация')
                  }
                }
              }}
              className="flex items-center justify-between p-3.5 rounded-2xl bg-rose-500/5 border border-rose-500/15 hover:bg-rose-500/10 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="size-8 rounded-lg bg-background flex items-center justify-center shadow-sm">
                  <Trash2 className="size-4 text-rose-500" />
                </div>
                <div className="text-left">
                  <h4 className="text-xs font-bold font-heading text-rose-500">
                    Удалить мой профиль и данные
                  </h4>
                  <p className="text-[10px] text-rose-500/60">
                    GDPR Art. 17 / 152-ФЗ ст. 21 — право на забвение
                  </p>
                </div>
              </div>
              <ChevronRight className="size-4 text-rose-500/40" />
            </motion.button>
          </div>
        </div>
      </section>
    </div>
  )
}
