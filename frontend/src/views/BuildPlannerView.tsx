import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useDocumentMeta } from '@/hooks/useDocumentMeta'
import { haptic } from '@/lib/haptic'
import {
  Award,
  Bookmark,
  Check,
  Copy,
  Flame,
  RefreshCw,
  Share2,
  Shield,
  Sparkles,
  Trophy,
  Zap,
} from '@/lib/icons'
import { getRankIcon, getRankName } from '@/lib/rankIcons'
import { motion } from 'framer-motion'
import { type FC, useEffect, useMemo, useState, useTransition } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

export interface SkillItem {
  id: string
  name: string
  icon: string
  element: 'fire' | 'lightning' | 'water' | 'earth' | 'neutral'
  type: string
  multiplier: number
  desc: string
}

export interface SpiritItem {
  id: string
  name: string
  icon: string
  element: string
  bonus: string
  multiplier: number
}

const AVAILABLE_SKILLS: SkillItem[] = [
  {
    id: 'rave',
    name: 'Rave (Рейв)',
    icon: '⚡',
    element: 'lightning',
    type: 'Buff',
    multiplier: 2.5,
    desc: '+150% скорость атаки и крит. шанс',
  },
  {
    id: 'rage',
    name: 'Rage (Ярость)',
    icon: '🔥',
    element: 'fire',
    type: 'Active',
    multiplier: 3.2,
    desc: 'Колоссальный взрывной урон',
  },
  {
    id: 'flame_wave',
    name: 'Flame Wave (Огненная волна)',
    icon: '🌋',
    element: 'fire',
    type: 'Active',
    multiplier: 2.8,
    desc: 'Периодический урон по площади',
  },
  {
    id: 'blitz_gold',
    name: 'Blitz Gold (Блиц Голд)',
    icon: '⚔️',
    element: 'neutral',
    type: 'Passive',
    multiplier: 2.1,
    desc: 'Увеличение урона и золота',
  },
  {
    id: 'fulgur',
    name: 'Fulgur (Молния)',
    icon: '🌩️',
    element: 'lightning',
    type: 'Active',
    multiplier: 2.9,
    desc: 'Цепная молния по группам врагов',
  },
  {
    id: 'blizzard',
    name: 'Blizzard (Метель)',
    icon: '❄️',
    element: 'water',
    type: 'AoE',
    multiplier: 2.4,
    desc: 'Замедление и урон холодом',
  },
  {
    id: 'golem',
    name: 'Golem Summon (Голем)',
    icon: '🗿',
    element: 'earth',
    type: 'Summon',
    multiplier: 1.8,
    desc: 'Танкование и дополнительный урон',
  },
  {
    id: 'meditate',
    name: 'Meditate (Медитация)',
    icon: '🧘',
    element: 'neutral',
    type: 'Buff',
    multiplier: 1.7,
    desc: 'Быстрая перезарядка всех навыков',
  },
  {
    id: 'supersonic',
    name: 'Supersonic (Сверхзвук)',
    icon: '💨',
    element: 'lightning',
    type: 'Active',
    multiplier: 2.6,
    desc: 'Рывок сквозь ряды монстров',
  },
  {
    id: 'immortal',
    name: 'Immortal (Бессмертие)',
    icon: '🛡️',
    element: 'neutral',
    type: 'Defensive',
    multiplier: 1.5,
    desc: 'Неуязвимость на 4 секунды',
  },
  {
    id: 'demon_hunt',
    name: 'Demon Hunt (Охота на демонов)',
    icon: '👹',
    element: 'fire',
    type: 'Passive',
    multiplier: 2.7,
    desc: '+80% урон по боссам',
  },
  {
    id: 'curse',
    name: 'Curse (Проклятие)',
    icon: '💀',
    element: 'neutral',
    type: 'Debuff',
    multiplier: 1.6,
    desc: 'Снижение защиты босса на 30%',
  },
]

const AVAILABLE_SPIRITS: SpiritItem[] = [
  {
    id: 'sala',
    name: 'Sala (Саламандра)',
    icon: '🔥',
    element: 'Огонь',
    bonus: '+25% Крит. урон',
    multiplier: 1.25,
  },
  {
    id: 'loia',
    name: 'Loia (Лоия)',
    icon: '🧚',
    element: 'Ветер',
    bonus: '+20% Базовая атака',
    multiplier: 1.2,
  },
  {
    id: 'noah',
    name: 'Noah (Ной)',
    icon: '🦅',
    element: 'Вода',
    bonus: '+18% Скорость атаки',
    multiplier: 1.18,
  },
  {
    id: 'radum',
    name: 'Radum (Радон)',
    icon: '🛡️',
    element: 'Земля',
    bonus: '+30% Защита и HP',
    multiplier: 1.15,
  },
  {
    id: 'todd',
    name: 'Todd (Тодд)',
    icon: '🐸',
    element: 'Вода',
    bonus: '+15% КД навыков',
    multiplier: 1.15,
  },
  {
    id: 'mum',
    name: 'Mum (Мум)',
    icon: '🦇',
    element: 'Тьма',
    bonus: '+22% Урон навыков',
    multiplier: 1.22,
  },
]

interface PresetBuild {
  id: string
  name: string
  icon: string
  description: string
  rank: number
  spirit: string
  skills: string[]
}

const PRESET_BUILDS: PresetBuild[] = [
  {
    id: 'bossing',
    name: 'Битва с Боссами',
    icon: '🐉',
    description: 'Максимальный взрывной урон по одиночным целям',
    rank: 16,
    spirit: 'sala',
    skills: ['rage', 'rave', 'demon_hunt', 'curse'],
  },
  {
    id: 'farming',
    name: 'Быстрый Фарм (Этапы)',
    icon: '⚡',
    description: 'Огромный AoE урон и скорость зачистки волн',
    rank: 12,
    spirit: 'loia',
    skills: ['fulgur', 'blizzard', 'blitz_gold', 'meditate'],
  },
  {
    id: 'rift',
    name: 'Разлом и Эфир',
    icon: '🌀',
    description: 'Сбалансированный сетап для закрытия разломов',
    rank: 18,
    spirit: 'noah',
    skills: ['supersonic', 'rave', 'flame_wave', 'golem'],
  },
  {
    id: 'survival',
    name: 'Пуш стадий (Выживание)',
    icon: '🛡️',
    description: 'Билд с защитой и бессмертием против ваншотов',
    rank: 14,
    spirit: 'radum',
    skills: ['immortal', 'rage', 'blitz_gold', 'golem'],
  },
]

export const BuildPlannerView: FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedRank, setSelectedRank] = useState<number>(
    () => Number(searchParams.get('rank')) || 12
  )
  const [selectedSpirit, setSelectedSpirit] = useState<string>(
    () => searchParams.get('spirit') || 'sala'
  )
  const [selectedSkills, setSelectedSkills] = useState<string[]>(() => {
    const fromUrl = searchParams.get('skills')
    return fromUrl ? fromUrl.split(',') : ['rage', 'rave', 'demon_hunt', 'blitz_gold']
  })
  const [copied, setCopied] = useState(false)
  const [, startTransition] = useTransition()

  useDocumentMeta({
    title: 'Калькулятор Билда и DPS',
    description: 'Интерактивный конструктор билдов, расчет урона и синергии духов Slayer Legend',
  })

  // Sync state with URL Search Params without page reload
  useEffect(() => {
    const params = new URLSearchParams()
    params.set('rank', String(selectedRank))
    params.set('spirit', selectedSpirit)
    params.set('skills', selectedSkills.join(','))
    setSearchParams(params, { replace: true })
  }, [selectedRank, selectedSpirit, selectedSkills, setSearchParams])

  const handleRankChange = (rank: number) => {
    startTransition(() => {
      setSelectedRank(rank)
    })
  }

  const handleSkillToggle = (skillId: string) => {
    haptic.light()
    startTransition(() => {
      setSelectedSkills((prev) => {
        if (prev.includes(skillId)) {
          return prev.filter((s) => s !== skillId)
        }
        if (prev.length >= 4) {
          toast.error('Максимум 4 активных навыка в билде!')
          return prev
        }
        return [...prev, skillId]
      })
    })
  }

  const applyPreset = (preset: PresetBuild) => {
    haptic.medium()
    startTransition(() => {
      setSelectedRank(preset.rank)
      setSelectedSpirit(preset.spirit)
      setSelectedSkills(preset.skills)
    })
    toast.success(`Пресет «${preset.name}» применён!`)
  }

  // Calculate estimated stats
  const calculatedStats = useMemo(() => {
    const baseAtk = 1000 + selectedRank * 450
    const rankBonus = selectedRank * 8.5
    const skillMultiplier = selectedSkills.reduce((acc, skillId) => {
      const found = AVAILABLE_SKILLS.find((s) => s.id === skillId)
      return acc + (found ? found.multiplier : 1.0)
    }, 1.0)

    const spiritObj = AVAILABLE_SPIRITS.find((s) => s.id === selectedSpirit)
    const spiritBonus = spiritObj ? spiritObj.multiplier : 1.0

    const totalDPS = Math.round(baseAtk * skillMultiplier * spiritBonus * (1 + rankBonus / 100))

    return {
      baseAtk,
      rankBonus: Math.round(rankBonus),
      totalDPS,
      skillCount: selectedSkills.length,
      spiritBonusLabel: spiritObj?.bonus || '+0%',
    }
  }, [selectedRank, selectedSpirit, selectedSkills])

  const handleShare = () => {
    haptic.medium()
    const params = new URLSearchParams()
    params.set('rank', String(selectedRank))
    params.set('spirit', selectedSpirit)
    params.set('skills', selectedSkills.join(','))

    const fullUrl = `${window.location.origin}/build?${params.toString()}`
    navigator.clipboard.writeText(fullUrl)
    setCopied(true)
    toast.success('Ссылка на калькулятор билда скопирована!')
    setTimeout(() => setCopied(false), 2500)
  }

  const handleCopyCard = () => {
    haptic.medium()
    const rankName = getRankName(selectedRank)
    const spiritName =
      AVAILABLE_SPIRITS.find((s) => s.id === selectedSpirit)?.name || selectedSpirit
    const skillNames = selectedSkills
      .map((sid) => AVAILABLE_SKILLS.find((s) => s.id === sid)?.name || sid)
      .join('\n• ')

    const cardText = `🗡️ **BlackRose Slayer Legend Build**\n━━━━━━━━━━━━━━━━━━━━\n🏆 **Промоушн:** ${rankName} (#${selectedRank})\n🧚 **Главный дух:** ${spiritName}\n⚔️ **Навыки:**\n• ${skillNames}\n💥 **Расчетный DPS:** ~${calculatedStats.totalDPS.toLocaleString('ru-RU')}\n━━━━━━━━━━━━━━━━━━━━\n📱 Открыть билд: ${window.location.origin}/build?rank=${selectedRank}&spirit=${selectedSpirit}&skills=${selectedSkills.join(',')}`

    navigator.clipboard.writeText(cardText)
    toast.success('Карточка билда скопирована для Discord / Telegram!')
  }

  return (
    <div className="flex flex-col min-h-full bg-background animate-in fade-in duration-300 pb-24">
      {/* Header */}
      <div className="p-4 sm:p-6 border-b border-border/10 bg-background/60 backdrop-blur-xl sticky top-0 z-30 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-foreground font-heading flex items-center gap-2">
            <Sparkles className="size-6 text-primary" />
            Калькулятор Билда
          </h1>
          <p className="text-xs text-muted-foreground font-medium mt-0.5">
            Конструктор экипировки, навыков и расчет урона Slayer Legend
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyCard}
            className="rounded-2xl border-rose-500/20 text-xs font-bold gap-1.5 hidden sm:flex"
          >
            <Copy className="size-3.5" />
            Карточка
          </Button>
          <Button
            size="sm"
            onClick={handleShare}
            className="rounded-2xl bg-primary text-white text-xs font-bold gap-1.5 shadow-lg shadow-rose-950/40"
          >
            {copied ? <Check className="size-3.5" /> : <Share2 className="size-3.5" />}
            Поделиться
          </Button>
        </div>
      </div>

      <div className="p-4 sm:p-6 space-y-8 max-w-5xl mx-auto w-full">
        {/* Preset Templates */}
        <div className="space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground font-heading">
            ⚡ Готовые пресеты билдов:
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {PRESET_BUILDS.map((preset) => (
              <button
                key={preset.id}
                type="button"
                onClick={() => applyPreset(preset)}
                className="flex flex-col p-3 rounded-2xl bg-card border border-border/10 hover:border-primary/40 hover:bg-primary/5 transition-all text-left group active:scale-95 shadow-sm"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xl">{preset.icon}</span>
                  <span className="text-xs font-bold text-foreground font-heading group-hover:text-primary transition-colors">
                    {preset.name}
                  </span>
                </div>
                <span className="text-[10px] text-muted-foreground/80 mt-1 line-clamp-1">
                  {preset.description}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* 1. DPS Stats Overview Card */}
        <Card className="card-elevated rounded-3xl border border-rose-500/20 overflow-hidden relative shadow-glow">
          <CardContent className="p-6 sm:p-8 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-5">
              <div className="size-16 sm:size-20 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center p-2 shrink-0">
                <img
                  src={getRankIcon(selectedRank)}
                  alt={getRankName(selectedRank)}
                  className="size-full object-contain drop-shadow-lg"
                />
              </div>
              <div>
                <Badge className="bg-primary/20 text-primary border-primary/30 text-[10px] font-bold uppercase tracking-wider">
                  Ранг {selectedRank} / 26
                </Badge>
                <h2 className="text-xl sm:text-2xl font-black text-foreground font-heading mt-1">
                  {getRankName(selectedRank)}
                </h2>
                <p className="text-xs text-muted-foreground font-medium">
                  Дух:{' '}
                  <span className="text-rose-300 font-bold">
                    {AVAILABLE_SPIRITS.find((s) => s.id === selectedSpirit)?.name}
                  </span>{' '}
                  ({calculatedStats.spiritBonusLabel})
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4 bg-muted/40 px-6 py-4 rounded-2xl border border-border/10 w-full sm:w-auto justify-around sm:justify-end">
              <div className="text-center sm:text-right">
                <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold font-heading">
                  Расчетный DPS
                </span>
                <div className="text-2xl sm:text-3xl font-black text-primary font-heading tracking-tight">
                  ~{calculatedStats.totalDPS.toLocaleString('ru-RU')}
                </div>
              </div>
              <div className="w-px h-10 bg-border/20" />
              <div className="text-center sm:text-right">
                <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold font-heading">
                  Бонус ранга
                </span>
                <div className="text-xl sm:text-2xl font-black text-amber-400 font-heading">
                  +{calculatedStats.rankBonus}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 2. Rank Selector Slider */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground font-heading">
              1. Выберите ступень промоушена (Ранг):
            </span>
            <span className="text-sm font-black text-primary font-heading">
              {getRankName(selectedRank)} (#{selectedRank})
            </span>
          </div>
          <input
            type="range"
            min={1}
            max={26}
            value={selectedRank}
            onChange={(e) => handleRankChange(Number(e.target.value))}
            className="w-full h-3 bg-muted/50 rounded-lg appearance-none cursor-pointer accent-primary"
          />
        </div>

        {/* 3. Spirits Selection */}
        <div className="space-y-3">
          <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground font-heading">
            2. Выберите духа-покровителя:
          </span>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
            {AVAILABLE_SPIRITS.map((spirit) => {
              const isSelected = selectedSpirit === spirit.id
              return (
                <button
                  key={spirit.id}
                  type="button"
                  onClick={() => {
                    haptic.selection()
                    setSelectedSpirit(spirit.id)
                  }}
                  className={`p-3.5 rounded-2xl border text-left transition-all flex flex-col justify-between gap-2 relative ${
                    isSelected
                      ? 'bg-primary/15 border-primary shadow-lg shadow-rose-950/30'
                      : 'bg-card/70 border-border/10 hover:border-border/30'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-2xl">{spirit.icon}</span>
                    <Badge variant="secondary" className="text-[9px] px-1.5 py-0 font-bold">
                      {spirit.element}
                    </Badge>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-foreground font-heading truncate">
                      {spirit.name}
                    </div>
                    <div className="text-[10px] text-rose-300/80 font-medium mt-0.5">
                      {spirit.bonus}
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* 4. Active Skills Selection */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground font-heading">
              3. Выберите активные навыки ({selectedSkills.length} / 4):
            </span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {AVAILABLE_SKILLS.map((skill) => {
              const isSelected = selectedSkills.includes(skill.id)
              return (
                <button
                  key={skill.id}
                  type="button"
                  onClick={() => handleSkillToggle(skill.id)}
                  className={`p-4 rounded-2xl border text-left transition-all flex items-start gap-3.5 relative ${
                    isSelected
                      ? 'bg-primary/15 border-primary shadow-md shadow-rose-950/30'
                      : 'bg-card/70 border-border/10 hover:border-border/30'
                  }`}
                >
                  <div className="size-11 rounded-xl bg-muted/40 border border-border/10 flex items-center justify-center text-xl shrink-0">
                    {skill.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="text-xs font-bold text-foreground font-heading truncate">
                        {skill.name}
                      </h4>
                      <Badge
                        variant="outline"
                        className="text-[9px] px-1.5 py-0 shrink-0 uppercase font-bold"
                      >
                        {skill.type}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-muted-foreground/80 mt-1 leading-snug">
                      {skill.desc}
                    </p>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
