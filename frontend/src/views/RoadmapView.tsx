import { Button } from '@/components/ui/button'
import { haptic } from '@/lib/haptic'
import { Sparkles } from '@/lib/icons'
import { motion } from 'framer-motion'
import type { FC } from 'react'

interface RoadmapViewProps {
  onSelectGuide?: (key: string) => void
}

export const RoadmapView: FC<RoadmapViewProps> = () => {
  return (
    <div className="view-scroll flex-1 overflow-y-auto px-5 py-6">
      <div className="flex flex-col gap-8 pb-32 max-w-md mx-auto stagger-in">
        {/* Intro Card */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="relative overflow-hidden rounded-[32px] border border-border/10 bg-muted/10 p-6 shadow-soft"
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
          className="rounded-[32px] border border-border/10 bg-card p-6 shadow-soft"
        >
          <layui-timeline>
            <layui-timeline-item time="Май 2026" title="Версия 3.3.0 — Премиальный дизайн">
              <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
                • ⚡ <strong>Новая типографика</strong>: Внедрена профессиональная пара шрифтов
                <strong> Manrope + Montserrat</strong> с идеальным отображением кириллицы на всех
                экранах.
                <br />• 🧭 <strong>Удобная навигация</strong>: Проектная карта перенесена в
                отдельный удобный раздел в шапке Mini App и браузера.
                <br />• 🧼 <strong>Чистота дашборда</strong>: Убрали лишнее дублирование категорий и
                блоков для более сфокусированного и эстетичного интерфейса.
                <br />• 🐛 <strong>Стабильность W3C</strong>: Исправлен баг двойной отрисовки
                элементов таймлайна при переходах.
              </p>
            </layui-timeline-item>

            <layui-timeline-item time="Апрель 2026" title="Версия 2.0.0 — Интеграция Layui">
              <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
                • 🛡️ <strong>Layui Web Components</strong>: Оптимизировано взаимодействие интерфейса
                на мобильных устройствах и десктопах.
                <br />• 🔑 <strong>Гостевой вход</strong>: Оптимизация авторизации для безбарьерного
                гостевого входа в Telegram Mini App.
              </p>
            </layui-timeline-item>

            <layui-timeline-item time="Март 2026" title="Версия 1.5.0 — Discord-Лаборатория">
              <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
                • 🧪 <strong>Синхронизация билдов</strong>: Добавлен раздел Discord-лаборатории для
                симуляции сражений.
                <br />• 💾 <strong>Кеширование данных</strong>: Улучшена скорость загрузки гайдов за
                счет адаптивного кеширования.
              </p>
            </layui-timeline-item>

            <layui-timeline-item time="В разработке" title="Будущие планы">
              <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
                • 📊 <strong>Калькуляторы характеристик</strong>: Интерактивный симулятор параметров
                снаряжения с наглядными графиками.
                <br />• 🌐 <strong>Интеграция с комьюнити</strong>: Возможность делиться своими
                сборками прямо в один клик.
              </p>
            </layui-timeline-item>
          </layui-timeline>
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
            <div className="size-16 rounded-[24px] bg-primary/10 flex items-center justify-center text-3xl shadow-soft">
              ❤️
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
              className="w-full h-12 rounded-2xl bg-primary text-primary-foreground font-black text-xs uppercase tracking-widest transition-all duration-300 hover:shadow-glow hover:scale-[1.02] active:scale-95"
              onClick={() => {
                haptic.medium()
                window.open('https://dalink.to/nihronick', '_blank')
              }}
            >
              Поддержать BlackRose
            </Button>
            <p className="text-[10px] font-bold text-muted-foreground/40 uppercase tracking-widest">
              BlackRose v3.3 • 2026
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default RoadmapView
