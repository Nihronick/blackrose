import { BrandIcon } from '@/components/ui/BrandIcon'
import { Button } from '@/components/ui/button'
import { APP_CONFIG } from '@/lib/constants'
import { haptic } from '@/lib/haptic'
import { Sparkles } from '@/lib/icons'
import { motion } from 'framer-motion'
import type { FC } from 'react'

interface RoadmapViewProps {
  onSelectGuide?: (key: string) => void
}

export const RoadmapView: FC<RoadmapViewProps> = () => {
  return (
    <div className="view-scroll flex-1 overflow-y-auto container-padding py-4 sm:py-6 relative z-0">
      <div className="absolute top-0 left-0 w-full h-80 mesh-bg opacity-30 pointer-events-none -z-10" />
      <div className="flex flex-col gap-6 sm:gap-8 pb-28 sm:pb-32 max-w-md mx-auto stagger-in relative z-10">
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
            {/* Vertical timeline line */}
            <div className="absolute left-[7px] top-2.5 bottom-2.5 w-[2px] bg-gradient-to-b from-primary via-violet-500/50 to-muted/20" />

            {[
              {
                time: 'Май 2026',
                title: 'Версия 3.3.0 — Премиальный дизайн',
                active: true,
                content: (
                  <ul className="space-y-1.5 mt-1 text-[11px] text-muted-foreground/90 leading-relaxed">
                    <li>
                      • ⚡ <strong>Новая типографика</strong>: Внедрена профессиональная пара
                      шрифтов <strong>Manrope + Montserrat</strong> с идеальным отображением
                      кириллицы на всех экранах.
                    </li>
                    <li>
                      • 🧭 <strong>Удобная навигация</strong>: Проектная карта перенесена в
                      отдельный раздел в шапке Mini App и браузера.
                    </li>
                    <li>
                      • 🧼 <strong>Чистота дашборда</strong>: Убрали лишнее дублирование категорий и
                      блоков для более сфокусированного и эстетичного интерфейса.
                    </li>
                    <li>
                      • 🐛 <strong>Стабильность W3C</strong>: Полностью исправили баг двойной
                      отрисовки элементов таймлайна при переходах.
                    </li>
                  </ul>
                ),
              },
              {
                time: 'Апрель 2026',
                title: 'Версия 2.0.0 — Оптимизация Mini App',
                active: false,
                content: (
                  <ul className="space-y-1.5 mt-1 text-[11px] text-muted-foreground/90 leading-relaxed">
                    <li>
                      • 🛡️ <strong>Интерфейс под мобильные</strong>: Оптимизировано взаимодействие
                      элементов на смартфонах и ПК-версиях.
                    </li>
                    <li>
                      • 🔑 <strong>Безбарьерный вход</strong>: Оптимизация авторизации для
                      мгновенного гостевого входа в Telegram Mini App.
                    </li>
                  </ul>
                ),
              },
              {
                time: 'Март 2026',
                title: 'Версия 1.5.0 — Discord-Лаборатория',
                active: false,
                content: (
                  <ul className="space-y-1.5 mt-1 text-[11px] text-muted-foreground/90 leading-relaxed">
                    <li>
                      • 🧪 <strong>Синхронизация билдов</strong>: Добавлен раздел
                      Discord-лаборатории для симуляции сражений.
                    </li>
                    <li>
                      • 💾 <strong>Кеширование данных</strong>: Улучшена скорость загрузки гайдов за
                      счет адаптивного кеширования.
                    </li>
                  </ul>
                ),
              },
              {
                time: 'В разработке',
                title: 'Будущие планы',
                pulsing: true,
                content: (
                  <ul className="space-y-1.5 mt-1 text-[11px] text-muted-foreground/90 leading-relaxed">
                    <li>
                      • 📊 <strong>Калькуляторы характеристик</strong>: Интерактивный симулятор
                      параметров снаряжения с наглядными графиками.
                    </li>
                    <li>
                      • 🌐 <strong>Интеграция с комьюнити</strong>: Возможность делиться своими
                      сборками прямо в один клик.
                    </li>
                  </ul>
                ),
              },
            ].map((item, index) => (
              <div key={index} className="relative flex flex-col gap-1.5">
                {/* Timeline node */}
                <div className="absolute -left-[31px] top-1 flex items-center justify-center">
                  {item.pulsing ? (
                    <div className="relative flex h-4 w-4">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                      <span className="relative inline-flex rounded-full h-4 w-4 bg-emerald-500 border-2 border-background" />
                    </div>
                  ) : item.active ? (
                    <div className="size-4 rounded-full bg-primary border-2 border-background shadow-glow animate-pulse" />
                  ) : (
                    <div className="size-4 rounded-full bg-muted-foreground/30 border-2 border-background" />
                  )}
                </div>

                {/* Time header */}
                <span
                  className={`text-[10px] font-black uppercase tracking-widest leading-none ${
                    item.active
                      ? 'text-primary'
                      : item.pulsing
                        ? 'text-emerald-400'
                        : 'text-muted-foreground/60'
                  }`}
                >
                  {item.time}
                </span>

                {/* Card Title */}
                <h4 className="text-[13px] font-black tracking-normal leading-snug font-heading text-foreground/90">
                  {item.title}
                </h4>

                {/* Content */}
                {item.content}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Premium Support Project Card */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="relative overflow-hidden rounded-[32px] border border-primary/20 bg-muted/15 p-6 shadow-glow transition-transform hover:scale-[1.01]"
        >
          {/* Neon Glow backgrounds */}
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

            {/* Social Brand Badges from thesvg */}
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
              <button
                type="button"
                className="size-10 rounded-xl bg-muted/30 border border-border/10 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-muted/60 transition-all duration-300"
                onClick={() => {
                  haptic.light()
                  window.open(APP_CONFIG.LINKS.BOOSTY, '_blank')
                }}
              >
                <BrandIcon name="boosty" size={20} />
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
