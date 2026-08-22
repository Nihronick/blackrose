import { Breadcrumbs } from '@/components/Breadcrumbs'
import { Card, CardContent } from '@/components/ui/card'
import { haptic } from '@/lib/haptic'
import { AlertCircle, FileText, Info, Lock, Mail, Scale, Shield, ShieldCheck } from '@/lib/icons'
import { motion } from 'framer-motion'
import { type FC, useState } from 'react'

type LegalTab = 'privacy' | 'terms' | 'disclaimer' | 'dmca'

export const LegalView: FC<{ initialTab?: LegalTab }> = ({ initialTab = 'privacy' }) => {
  const [activeTab, setActiveTab] = useState<LegalTab>(initialTab)

  const tabs: { id: LegalTab; label: string; icon: typeof Shield }[] = [
    { id: 'privacy', label: '152-ФЗ / GDPR', icon: Shield },
    { id: 'terms', label: 'Соглашение', icon: FileText },
    { id: 'disclaimer', label: 'Дисклеймер', icon: Info },
    { id: 'dmca', label: 'DMCA / Правообладатели', icon: Scale },
  ]

  return (
    <div className="flex flex-col min-h-full bg-background pb-24 animate-in fade-in duration-300">
      <div className="container-padding pt-6 max-w-4xl mx-auto w-full space-y-6">
        <Breadcrumbs
          items={[{ label: 'Главная', route: { type: 'home' } }, { label: 'Правовая информация' }]}
        />

        {/* Header */}
        <div className="p-6 sm:p-8 rounded-3xl rose-bento-card border border-rose-500/20 bg-gradient-to-br from-card/90 via-card/70 to-rose-950/20 shadow-2xl">
          <div className="flex items-center gap-3 mb-2">
            <div className="size-10 rounded-xl bg-primary/20 text-primary flex items-center justify-center border border-primary/30">
              <Scale className="size-5" />
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-black font-heading text-foreground">
                Правовая информация и Политики
              </h1>
              <p className="text-xs text-muted-foreground font-medium">
                Юридическая прозрачность, защита персональных данных (152-ФЗ / GDPR) и правила
                проекта
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 mt-6 overflow-x-auto no-scrollbar pb-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    haptic.selection()
                    setActiveTab(tab.id)
                  }}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-2xl text-xs font-bold font-heading uppercase tracking-wider transition-all whitespace-nowrap border ${
                    isActive
                      ? 'bg-primary text-white border-primary shadow-lg shadow-rose-950/50 scale-[1.02]'
                      : 'bg-card/60 text-muted-foreground hover:text-foreground hover:bg-card border-border/10'
                  }`}
                >
                  <Icon className="size-3.5" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Tab Content */}
        <Card className="rounded-3xl border border-border/10 bg-card/60 backdrop-blur-xl shadow-xl overflow-hidden">
          <CardContent className="p-6 sm:p-8 space-y-6 leading-relaxed text-foreground/90 text-sm">
            {activeTab === 'privacy' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-2 text-primary font-bold font-heading text-lg border-b border-border/10 pb-3">
                  <ShieldCheck className="size-5" />
                  <h2>Политика конфиденциальности (152-ФЗ РФ & EU GDPR 2016/679)</h2>
                </div>

                <div className="bg-primary/5 border border-primary/20 rounded-2xl p-4 text-xs space-y-2">
                  <p className="font-semibold text-foreground">
                    📌 Ключевые принципы обработки данных:
                  </p>
                  <p>
                    Проект <strong>BlackRose</strong> уважает право на неприкосновенность частной
                    жизни и строго соблюдает Федеральный закон РФ № 152-ФЗ «О персональных данных» и
                    Генеральный регламент ЕС по защите данных (GDPR).
                  </p>
                </div>

                <div className="space-y-4">
                  <h3 className="text-base font-bold font-heading text-rose-300">
                    1. Какие данные мы собираем
                  </h3>
                  <ul className="list-disc pl-5 space-y-1 text-xs text-muted-foreground">
                    <li>
                      <strong>Telegram ID, имя и username:</strong> собираются исключительно при
                      добровольной авторизации через Telegram Login / Mini App для персонализации
                      профиля.
                    </li>
                    <li>
                      <strong>Избранное и история чтения:</strong> сохраняются локально в вашем
                      браузере (LocalStorage) и синхронизируются с защищенной базой данных только
                      для авторизованных пользователей.
                    </li>
                    <li>
                      <strong>Реакции и комментарии:</strong> привязаны к вашему профилю для защиты
                      от спама и поддержания порядка в сообществе.
                    </li>
                    <li>
                      Мы <strong>НЕ</strong> собираем пароли от ваших игровых аккаунтов, платежные
                      данные, номера банковских карт, номера телефонов или паспортные данные.
                    </li>
                  </ul>

                  <h3 className="text-base font-bold font-heading text-rose-300">
                    2. Цели сбора и правовые основания
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Обработка данных осуществляется на основании согласия пользователя (ст. 6 152-ФЗ
                    / Art. 6 GDPR) исключительно для предоставления доступа к функционалу базы
                    знаний (калькулятор билдов, закладки, рейтинги гильдий).
                  </p>

                  <h3 className="text-base font-bold font-heading text-rose-300">
                    3. Права пользователей (ст. 14, 21 152-ФЗ & Art. 17, 20 GDPR)
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                    <div className="p-4 rounded-2xl bg-muted/20 border border-border/10 space-y-1">
                      <h4 className="font-bold text-foreground text-xs font-heading">
                        📥 Право на выгрузку (Data Portability)
                      </h4>
                      <p className="text-[11px] text-muted-foreground">
                        Вы можете в любой момент выгрузить все ваши персональные данные в
                        машиночитаемом формате JSON в настройках профиля.
                      </p>
                    </div>
                    <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 space-y-1">
                      <h4 className="font-bold text-rose-400 text-xs font-heading">
                        🗑️ Право на забвение (Right to Erasure)
                      </h4>
                      <p className="text-[11px] text-muted-foreground">
                        Вы можете в один клик полностью и безвозвратно удалить свой аккаунт,
                        историю, закладки и реакции из базы данных.
                      </p>
                    </div>
                  </div>

                  <h3 className="text-base font-bold font-heading text-rose-300">
                    4. Контакты оператора данных
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    По всем вопросам защиты персональных данных вы можете обратиться напрямую:
                    Telegram: <code>@nihronick</code>.
                  </p>
                </div>
              </motion.div>
            )}

            {activeTab === 'terms' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-2 text-primary font-bold font-heading text-lg border-b border-border/10 pb-3">
                  <FileText className="size-5" />
                  <h2>Пользовательское соглашение (Terms of Service)</h2>
                </div>

                <div className="space-y-4 text-xs text-muted-foreground">
                  <h3 className="text-sm font-bold font-heading text-foreground">
                    1. Общие положения
                  </h3>
                  <p>
                    Настоящее Соглашение регулирует использование веб-сайта и Telegram Mini App{' '}
                    <strong>BlackRose</strong>. Используя сайт, вы выражаете полное согласие с
                    настоящими условиями.
                  </p>

                  <h3 className="text-sm font-bold font-heading text-foreground">
                    2. Статус ресурса
                  </h3>
                  <p>
                    BlackRose является бесплатной, некоммерческой фанатской базой знаний (Fan-made
                    Community Wiki), созданной игроками для сообщества игроков Slayer Legend. Проект
                    не является официальным сайтом игры.
                  </p>

                  <h3 className="text-sm font-bold font-heading text-foreground">
                    3. Правила поведения и комментариев
                  </h3>
                  <p>В сообществе запрещены:</p>
                  <ul className="list-disc pl-5 space-y-1">
                    <li>Оскорбления, разжигание ненависти, публикация спама или рекламы;</li>
                    <li>
                      Попытки взлома, DDoS-атак, несанкционированного доступа к административным
                      функциям;
                    </li>
                    <li>Распространение вредоносного ПО или фишинговых ссылок.</li>
                  </ul>

                  <h3 className="text-sm font-bold font-heading text-foreground">
                    4. Ограничение ответственности
                  </h3>
                  <p>
                    Все игровые данные, формулы расчёта DPS, гайды и рекомендации предоставляются
                    «как есть» (AS IS). Администрация не гарантирует абсолютную безошибочность
                    игровых механик в связи с регулярными патчами и обновлениями игры.
                  </p>
                </div>
              </motion.div>
            )}

            {activeTab === 'disclaimer' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-2 text-primary font-bold font-heading text-lg border-b border-border/10 pb-3">
                  <Info className="size-5" />
                  <h2>Дисклеймер об авторских правах и товарных знаках</h2>
                </div>

                <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-4 text-xs space-y-2 text-amber-200">
                  <p className="font-bold flex items-center gap-2">
                    <AlertCircle className="size-4 text-amber-400" />
                    Неофициальный фанатский проект (Fan Content)
                  </p>
                  <p>
                    Все названия, изображения, иконки навыков, персонажей и логотипы игры{' '}
                    <strong>Slayer Legend</strong> принадлежат их законным владельцам и
                    правообладателям — компании <strong>GEAR2PLAY Co., Ltd.</strong>
                  </p>
                </div>

                <div className="space-y-3 text-xs text-muted-foreground">
                  <p>
                    Использование графических и текстовых материалов игры осуществляется в
                    информационных, образовательных и исследовательских целях в соответствии с
                    концепцией <strong>Fair Use</strong> (добросовестное использование)
                    законодательства об авторском праве.
                  </p>
                  <p>
                    Проект BlackRose не претендует на интеллектуальную собственность разработчиков и
                    не является аффилированным лицом GEAR2PLAY Co., Ltd.
                  </p>
                </div>
              </motion.div>
            )}

            {activeTab === 'dmca' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <div className="flex items-center gap-2 text-primary font-bold font-heading text-lg border-b border-border/10 pb-3">
                  <Scale className="size-5" />
                  <h2>DMCA / Уведомления правообладателей (Notice & Takedown)</h2>
                </div>

                <div className="space-y-4 text-xs text-muted-foreground">
                  <p>
                    Мы с глубоким уважением относимся к правам интеллектуальной собственности. Если
                    вы являетесь правообладателем и считаете, что какой-либо контент на нашем сайте
                    нарушает ваши авторские права, свяжитесь с нами для оперативного удаления или
                    изменения материала.
                  </p>

                  <div className="p-4 rounded-2xl bg-card border border-primary/20 space-y-2">
                    <h3 className="font-bold text-foreground text-xs font-heading">
                      📧 Как направить запрос:
                    </h3>
                    <p>
                      Отправьте сообщение с темой <em>«DMCA / Запрос правообладателя»</em>, указав:
                    </p>
                    <ul className="list-disc pl-5 space-y-1">
                      <li>Прямую ссылку на страницу со спорным материалом;</li>
                      <li>
                        Документальное подтверждение ваших прав на объект интеллектуальной
                        собственности;
                      </li>
                      <li>Ваши контактные данные для обратной связи.</li>
                    </ul>
                    <div className="pt-2 flex items-center gap-2 text-primary font-bold">
                      <Mail className="size-4" />
                      <span>Telegram: @nihronick</span>
                    </div>
                  </div>

                  <p className="text-[11px] text-muted-foreground/70">
                    Срок рассмотрения и обработки обоснованных обращений правообладателей составляет
                    не более 24–48 рабочих часов.
                  </p>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
