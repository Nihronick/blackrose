import { BrandIcon } from '@/components/ui/BrandIcon'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { APP_CONFIG } from '@/lib/constants'
import { haptic } from '@/lib/haptic'
import { Flame, Shield, Sparkles, Trophy, Zap } from '@/lib/icons'
import { motion } from 'framer-motion'
import { type FC, useState } from 'react'

interface RoadmapViewProps {
  onSelectGuide?: (key: string) => void
}

const TIER_LIST_DATA = {
  spirits: [
    {
      tier: 'S',
      color: 'from-amber-500/30 to-amber-950/40 border-amber-500/50 text-amber-400',
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      items: [
        {
          name: 'Sala (Саламандра)',
          icon: '🔥',
          desc: '+25% Крит. урон, топ-1 для боссов и соло-целей',
          guideKey: 'discord_1266502911324721335',
        },
        {
          name: 'Loia (Лоия)',
          icon: '🧚',
          desc: '+20% Базовая атака, абсолютный мета-дух для фарма стадий',
          guideKey: 'discord_1266502911324721335',
        },
      ],
    },
    {
      tier: 'A',
      color: 'from-rose-500/30 to-rose-950/40 border-rose-500/50 text-rose-400',
      badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
      items: [
        {
          name: 'Noah (Ной)',
          icon: '🦅',
          desc: '+18% Скорость атаки, универсален для Разлома и Эфира',
          guideKey: 'discord_1266502911324721335',
        },
        {
          name: 'Mum (Мум)',
          icon: '🦇',
          desc: '+22% Урон навыков, мощный бафф для бурст-прокастов',
          guideKey: 'discord_1266502911324721335',
        },
      ],
    },
    {
      tier: 'B',
      color: 'from-blue-500/30 to-blue-950/40 border-blue-500/50 text-blue-400',
      badgeColor: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
      items: [
        {
          name: 'Todd (Тодд)',
          icon: '🐸',
          desc: '+15% КД навыков, полезен на затяжных боссах',
          guideKey: 'discord_1266502911324721335',
        },
        {
          name: 'Radum (Радон)',
          icon: '🛡️',
          desc: '+30% Защита, спасает от ваншотов на высоких стадиях',
          guideKey: 'discord_1266502911324721335',
        },
      ],
    },
  ],
  skills: [
    {
      tier: 'S',
      color: 'from-amber-500/30 to-amber-950/40 border-amber-500/50 text-amber-400',
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
      items: [
        {
          name: 'Rage (Ярость)',
          icon: '🔥',
          desc: 'Огромный множитель урона',
          guideKey: 'discord_1266502911324721335',
        },
        {
          name: 'Rave (Рейв)',
          icon: '⚡',
          desc: 'Ускорение атаки и крит. удары',
          guideKey: 'discord_1266502911324721335',
        },
        {
          name: 'Fulgur (Молния)',
          icon: '🌩️',
          desc: 'Цепная зачистка всех волн',
          guideKey: 'discord_1266502911324721335',
        },
      ],
    },
    {
      tier: 'A',
      color: 'from-rose-500/30 to-rose-950/40 border-rose-500/50 text-rose-400',
      badgeColor: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
      items: [
        {
          name: 'Flame Wave (Огненная волна)',
          icon: '🌋',
          desc: 'AoE горение',
          guideKey: 'discord_1266502911324721335',
        },
        {
          name: 'Demon Hunt (Охота на демонов)',
          icon: '👹',
          desc: 'Урон по боссам',
          guideKey: 'discord_1266502911324721335',
        },
        {
          name: 'Blizzard (Метель)',
          icon: '❄️',
          desc: 'Замедление и контроль',
          guideKey: 'discord_1266502911324721335',
        },
      ],
    },
  ],
}

export const RoadmapView: FC<RoadmapViewProps> = ({ onSelectGuide }) => {
  const [activeTab, setActiveTab] = useState<'roadmap' | 'tierlist'>('roadmap')

  return (
    <div className="view-scroll flex-1 overflow-y-auto container-padding py-4 sm:py-6 relative z-0">
      <div className="absolute top-0 left-0 w-full h-80 mesh-bg opacity-30 pointer-events-none -z-10" />
      <div className="flex flex-col gap-6 sm:gap-8 pb-28 sm:pb-32 max-w-xl mx-auto stagger-in relative z-10">
        {/* Navigation Tabs */}
        <div className="flex items-center justify-center p-1 bg-card/60 backdrop-blur-xl rounded-2xl border border-border/10 shadow-sm">
          <button
            type="button"
            onClick={() => {
              haptic.selection()
              setActiveTab('roadmap')
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-bold font-heading transition-all ${
              activeTab === 'roadmap'
                ? 'bg-primary text-white shadow-md shadow-rose-950/30'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            📅 Дорожная карта
          </button>
          <button
            type="button"
            onClick={() => {
              haptic.selection()
              setActiveTab('tierlist')
            }}
            className={`flex-1 py-2 rounded-xl text-xs font-bold font-heading transition-all ${
              activeTab === 'tierlist'
                ? 'bg-primary text-white shadow-md shadow-rose-950/30'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            🏆 Тир-лист меты
          </button>
        </div>

        {activeTab === 'tierlist' ? (
          /* Tier List Tab Content */
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-8"
          >
            {/* Spirits Tier List */}
            <div className="space-y-4">
              <h3 className="text-base font-black text-foreground font-heading flex items-center gap-2">
                <Sparkles className="size-5 text-amber-400" />
                Тир-лист Духов (Spirits Meta)
              </h3>
              <div className="space-y-3">
                {TIER_LIST_DATA.spirits.map((group) => (
                  <div
                    key={group.tier}
                    className={`rounded-2xl p-4 border bg-gradient-to-r ${group.color} flex flex-col gap-2.5 shadow-md`}
                  >
                    <div className="flex items-center gap-2">
                      <Badge className={`text-xs font-black px-2.5 py-0.5 ${group.badgeColor}`}>
                        Tier {group.tier}
                      </Badge>
                      <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
                        {group.tier === 'S'
                          ? 'Обязательный пик'
                          : group.tier === 'A'
                            ? 'Сильная мета'
                            : 'Ситуативный выбор'}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1">
                      {group.items.map((item) => (
                        <div
                          key={item.name}
                          onClick={() => {
                            haptic.light()
                            if (onSelectGuide && item.guideKey) onSelectGuide(item.guideKey)
                          }}
                          className="flex items-start gap-2.5 p-2.5 rounded-xl bg-background/50 border border-border/10 hover:border-primary/40 cursor-pointer transition-all active:scale-95"
                        >
                          <span className="text-2xl shrink-0">{item.icon}</span>
                          <div className="min-w-0 flex-1">
                            <h4 className="text-xs font-bold text-foreground font-heading truncate">
                              {item.name}
                            </h4>
                            <p className="text-[10px] text-muted-foreground/90 mt-0.5 leading-snug">
                              {item.desc}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Skills Tier List */}
            <div className="space-y-4">
              <h3 className="text-base font-black text-foreground font-heading flex items-center gap-2">
                <Zap className="size-5 text-primary" />
                Тир-лист Навыков (Skills Meta)
              </h3>
              <div className="space-y-3">
                {TIER_LIST_DATA.skills.map((group) => (
                  <div
                    key={group.tier}
                    className={`rounded-2xl p-4 border bg-gradient-to-r ${group.color} flex flex-col gap-2.5 shadow-md`}
                  >
                    <div className="flex items-center gap-2">
                      <Badge className={`text-xs font-black px-2.5 py-0.5 ${group.badgeColor}`}>
                        Tier {group.tier}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-1">
                      {group.items.map((item) => (
                        <div
                          key={item.name}
                          onClick={() => {
                            haptic.light()
                            if (onSelectGuide && item.guideKey) onSelectGuide(item.guideKey)
                          }}
                          className="flex items-start gap-2 p-2 rounded-xl bg-background/50 border border-border/10 hover:border-primary/40 cursor-pointer transition-all active:scale-95"
                        >
                          <span className="text-xl shrink-0">{item.icon}</span>
                          <div className="min-w-0 flex-1">
                            <h4 className="text-xs font-bold text-foreground font-heading truncate">
                              {item.name}
                            </h4>
                            <p className="text-[10px] text-muted-foreground/80 mt-0.5 leading-snug line-clamp-2">
                              {item.desc}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        ) : (
          /* Roadmap Tab Content */
          <>
            {/* Intro Card */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="card-elevated relative overflow-hidden rounded-3xl p-5 sm:p-6"
            >
              <div className="absolute -right-6 -top-6 size-24 rounded-full bg-primary/10 blur-[40px]" />
              <h2 className="text-lg font-black tracking-tight text-foreground flex items-center gap-2 mb-2">
                <Sparkles className="size-5 text-primary animate-pulse" />
                Дорожная карта
              </h2>
              <p className="text-xs font-medium text-muted-foreground/80 leading-relaxed">
                Мы постоянно развиваем базу знаний BlackRose, адаптируя интерфейс для максимального
                удобства на смартфонах и ПК. Следите за обновлениями и нашими планами ниже!
              </p>
            </motion.div>

            {/* Timeline Block */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card-elevated rounded-3xl p-5 sm:p-6 relative overflow-hidden"
            >
              <div className="relative flex flex-col gap-8 pl-8">
                <div className="absolute left-[7px] top-2.5 bottom-2.5 w-[2px] bg-gradient-to-b from-primary via-violet-500/50 to-muted/20" />

                {[
                  {
                    time: 'Август 2026',
                    title: 'Версия 4.0.0 — PWA, Офлайн и Telegram-бот',
                    active: true,
                    content: (
                      <ul className="space-y-1.5 mt-1 text-[11px] text-muted-foreground/90 leading-relaxed">
                        <li>
                          • 📱 <strong>PWA & Offline</strong>: Service Worker кэширует гайды и
                          медиафайлы.
                        </li>
                        <li>
                          • 🔥 <strong>Живые реакции</strong>: Реальные счетчики лайков и реакций в
                          БД.
                        </li>
                        <li>
                          • ☁️ <strong>Облачное избранное</strong>: Автоматическая синхронизация
                          между устройствами.
                        </li>
                        <li>
                          • 🤖 <strong>Telegram-бот</strong>: Поддержка Mini App и push-уведомлений.
                        </li>
                      </ul>
                    ),
                  },
                  {
                    time: 'Май 2026',
                    title: 'Версия 3.3.0 — Премиальный дизайн',
                    active: false,
                    content: (
                      <ul className="space-y-1.5 mt-1 text-[11px] text-muted-foreground/90 leading-relaxed">
                        <li>
                          • ⚡ <strong>Новая типографика</strong>: Внедрены шрифты Inter и Outfit.
                        </li>
                        <li>
                          • 🧭 <strong>Удобная навигация</strong>: Проектная карта и быстрый доступ.
                        </li>
                        <li>
                          • 🧼 <strong>Чистота дашборда</strong>: Строгий список из 14 официальных
                          категорий.
                        </li>
                      </ul>
                    ),
                  },
                ].map((item) => (
                  <div key={item.title} className="relative flex flex-col gap-1">
                    <div
                      className={`absolute -left-[31px] top-1 size-3.5 rounded-full border-2 bg-background flex items-center justify-center transition-all ${
                        item.active
                          ? 'border-primary shadow-[0_0_12px_rgba(225,29,72,0.8)] scale-125'
                          : 'border-muted-foreground/40'
                      }`}
                    >
                      {item.active && <div className="size-1.5 rounded-full bg-primary" />}
                    </div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                      {item.time}
                    </span>
                    <h4 className="text-[13px] font-black leading-snug font-heading text-foreground/90">
                      {item.title}
                    </h4>
                    {item.content}
                  </div>
                ))}
              </div>
            </motion.div>
          </>
        )}

        {/* Support Project Card */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative overflow-hidden rounded-[32px] border border-primary/20 bg-muted/15 p-6 shadow-glow transition-transform hover:scale-[1.01]"
        >
          <div className="absolute -left-10 -bottom-10 size-32 rounded-full bg-primary/10 blur-[50px]" />
          <div className="absolute -right-10 -top-10 size-32 rounded-full bg-primary/25 blur-[55px]" />

          <div className="relative z-10 flex flex-col items-center text-center gap-4">
            <div className="size-16 rounded-[24px] bg-primary/10 flex items-center justify-center shadow-soft">
              <BrandIcon name="patreon" size={32} className="text-primary animate-pulse" />
            </div>
            <div className="flex flex-col gap-1">
              <h3 className="text-base font-black tracking-tight text-foreground uppercase">
                Поддержать проект
              </h3>
              <p className="text-xs font-medium text-muted-foreground/90 leading-relaxed max-w-[280px]">
                Разработка и поддержка BlackRose ведется силами комьюнити. Каждая лепта помогает
                оплачивать серверы и делать проект лучше!
              </p>
            </div>
            <Button
              className="w-full h-12 rounded-2xl bg-primary text-primary-foreground font-black text-xs uppercase tracking-widest transition-all duration-300 hover:shadow-glow hover:scale-[1.02] active:scale-95 flex items-center justify-center gap-2"
              onClick={() => {
                haptic.medium()
                window.open(APP_CONFIG.LINKS.DONATE, '_blank')
              }}
            >
              <BrandIcon name="qiwi" size={16} />
              Поддержать BlackRose
            </Button>

            <div className="flex items-center gap-3 mt-2">
              <button
                type="button"
                className="size-10 rounded-xl bg-muted/30 border border-border/10 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all duration-300"
                onClick={() => {
                  haptic.light()
                  window.open(APP_CONFIG.LINKS.TELEGRAM, '_blank')
                }}
              >
                <BrandIcon name="telegram" size={20} />
              </button>
              <button
                type="button"
                className="size-10 rounded-xl bg-muted/30 border border-border/10 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all duration-300"
                onClick={() => {
                  haptic.light()
                  window.open(APP_CONFIG.LINKS.DISCORD, '_blank')
                }}
              >
                <BrandIcon name="discord" size={20} />
              </button>
              <button
                type="button"
                className="size-10 rounded-xl bg-muted/30 border border-border/10 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all duration-300"
                onClick={() => {
                  haptic.light()
                  window.open(APP_CONFIG.LINKS.GITHUB, '_blank')
                }}
              >
                <BrandIcon name="github" size={20} />
              </button>
            </div>

            <p className="text-[10px] font-bold text-muted-foreground/40 uppercase tracking-widest mt-2">
              {APP_CONFIG.PROJECT_NAME} v{APP_CONFIG.VERSION} • {APP_CONFIG.YEAR}
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
