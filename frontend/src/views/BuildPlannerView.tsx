import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { haptic } from '@/lib/haptic'
import { Award, Check, Copy, Flame, RefreshCw, Share2, Shield, Sparkles, Zap } from '@/lib/icons'
import { getRankIcon, getRankName } from '@/lib/rankIcons'
import { motion } from 'framer-motion'
import { type FC, useEffect, useMemo, useState, useTransition } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

const AVAILABLE_SKILLS = [
  { id: 'rave', name: 'Rave (Рейв)', icon: '⚡', type: 'Buff', multiplier: 2.5 },
  { id: 'rage', name: 'Rage (Ярость)', icon: '🔥', type: 'Active', multiplier: 3.0 },
  { id: 'golem', name: 'Golem Summon (Голем)', icon: '🗿', type: 'Summon', multiplier: 1.8 },
  { id: 'blitz_gold', name: 'Blitz Gold (Блиц Голд)', icon: '⚔️', type: 'Passive', multiplier: 2.1 },
  { id: 'curse', name: 'Curse (Проклятие)', icon: '💀', type: 'Debuff', multiplier: 1.5 },
  {
    id: 'flame_slash',
    name: 'Flame Slash (Огненный Взмах)',
    icon: '🗡️',
    type: 'Active',
    multiplier: 2.2,
  },
]

const AVAILABLE_SPIRITS = [
  { id: 'loia', name: 'Loia (Лоия)', icon: '🧚', bonus: '+15% Атака' },
  { id: 'sala', name: 'Sala (Сала)', icon: '🔥', bonus: '+20% Крит. урон' },
  { id: 'todd', name: 'Todd (Тодд)', icon: '🐸', bonus: '+12% Перезарядка' },
  { id: 'noah', name: 'Noah (Ной)', icon: '🦅', bonus: '+18% Скорость атаки' },
]

export const BuildPlannerView: FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedRank, setSelectedRank] = useState<number>(
    () => Number(searchParams.get('rank')) || 12
  )
  const [selectedSpirit, setSelectedSpirit] = useState<string>(
    () => searchParams.get('spirit') || 'loia'
  )
  const [selectedSkills, setSelectedSkills] = useState<string[]>(() => {
    const fromUrl = searchParams.get('skills')
    return fromUrl ? fromUrl.split(',') : ['rave', 'rage', 'golem', 'blitz_gold']
  })
  const [copied, setCopied] = useState(false)
  const [isPending, startTransition] = useTransition()

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

  // Calculate estimated stats
  const calculatedStats = useMemo(() => {
    const baseAtk = 1000 + selectedRank * 450
    const rankBonus = selectedRank * 8.5
    const skillMultiplier = selectedSkills.reduce((acc, skillId) => {
      const found = AVAILABLE_SKILLS.find((s) => s.id === skillId)
      return acc + (found ? found.multiplier : 1.0)
    }, 1.0)

    const spiritObj = AVAILABLE_SPIRITS.find((s) => s.id === selectedSpirit)
    const spiritBonus = spiritObj ? 1.15 : 1.0

    const totalDPS = Math.round(baseAtk * skillMultiplier * spiritBonus * (1 + rankBonus / 100))

    return {
      baseAtk,
      rankBonus: Math.round(rankBonus),
      totalDPS,
      skillCount: selectedSkills.length,
    }
  }, [selectedRank, selectedSpirit, selectedSkills])

  const toggleSkill = (skillId: string) => {
    haptic.light()
    if (selectedSkills.includes(skillId)) {
      setSelectedSkills(selectedSkills.filter((s) => s !== skillId))
    } else {
      if (selectedSkills.length >= 4) {
        toast.error('Максимум 4 активных навыка в билде!')
        return
      }
      setSelectedSkills([...selectedSkills, skillId])
    }
  }

  const handleShare = () => {
    haptic.medium()
    const params = new URLSearchParams()
    params.set('rank', String(selectedRank))
    params.set('spirit', selectedSpirit)
    params.set('skills', selectedSkills.join(','))

    const fullUrl = `${window.location.origin}/build-planner?${params.toString()}`
    navigator.clipboard.writeText(fullUrl)
    setCopied(true)
    toast.success('Ссылка на калькулятор билда скопирована!')
    setTimeout(() => setCopied(false), 2500)
  }

  return (
    <div className="w-full max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-10 xl:px-12 py-6 space-y-8 animate-in fade-in duration-500 rose-mesh-bg rounded-3xl">
      {/* Header Banner */}
      <div className="relative overflow-hidden rounded-3xl p-6 sm:p-8 rose-bento-card border-rose-500/30 bg-gradient-to-br from-rose-950/50 via-card/70 to-card/90 shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="gold-accent-badge">
                <Sparkles className="size-3.5 fill-amber-400" />
                <span>Interactive Tool v2.0</span>
              </div>
              <span className="text-xs font-bold text-rose-400/80">• Slayer Legend Builder</span>
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black uppercase tracking-tight font-heading text-foreground">
              Калькулятор Билда & Промоутов
            </h1>
            <p className="text-xs sm:text-sm font-medium text-muted-foreground max-w-xl">
              Настраивайте ранги промоута, подбирайте духов и комбо навыков. Считайте DPS и делитесь
              готовым билдом с согильдийцами!
            </p>
          </div>

          <Button
            size="lg"
            className="rose-glow-btn h-12 px-6 text-xs gap-2 shrink-0"
            onClick={handleShare}
          >
            {copied ? <Check className="size-4" /> : <Share2 className="size-4" />}
            {copied ? 'Скопировано!' : 'Поделиться Билдом'}
          </Button>
        </div>
      </div>

      {/* Grid Content */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        {/* Left Control Panel */}
        <div className="xl:col-span-7 space-y-6">
          {/* Rank Selector */}
          <Card className="p-6 border border-rose-500/20 rose-bento-card rounded-3xl space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Award className="size-5 text-rose-400" />
                <h3 className="text-sm font-black uppercase font-heading tracking-wide text-foreground">
                  Ранг Промоута (Ранг {selectedRank})
                </h3>
              </div>
              <span className="text-xs font-bold text-amber-400 font-mono gold-accent-badge">
                {getRankName(selectedRank)}
              </span>
            </div>

            <div className="flex items-center gap-4 bg-background/50 p-4 rounded-2xl border border-white/10">
              {getRankIcon(selectedRank) && (
                <img
                  src={getRankIcon(selectedRank)}
                  alt={getRankName(selectedRank)}
                  className="size-12 object-contain shrink-0 drop-shadow-md"
                />
              )}
              <div className="flex-1 space-y-2">
                <input
                  type="range"
                  min="1"
                  max="21"
                  value={selectedRank}
                  onChange={(e) => handleRankChange(Number(e.target.value))}
                  className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-rose-500"
                />
                <div className="flex justify-between text-[10px] font-bold text-muted-foreground font-mono">
                  <span>1 (Stone)</span>
                  <span>11 (Diadust)</span>
                  <span>21 (Infinaut)</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Skill Selector */}
          <Card className="p-6 border border-rose-500/20 rose-bento-card rounded-3xl space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Flame className="size-5 text-amber-400" />
                <h3 className="text-sm font-black uppercase font-heading tracking-wide text-foreground">
                  Активные Навыки ({selectedSkills.length} / 4)
                </h3>
              </div>
              <span className="text-[10px] font-bold text-rose-400 uppercase">
                Выберите 4 навыка
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {AVAILABLE_SKILLS.map((skill) => {
                const active = selectedSkills.includes(skill.id)
                return (
                  <motion.div
                    key={skill.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.96 }}
                    onClick={() => toggleSkill(skill.id)}
                    className={`p-3.5 rounded-2xl border cursor-pointer transition-all flex items-center gap-3 ${
                      active
                        ? 'bg-primary/20 border-primary text-foreground shadow-md shadow-primary/10'
                        : 'bg-background/40 border-border/10 text-muted-foreground hover:bg-muted/30'
                    }`}
                  >
                    <span className="text-xl">{skill.icon}</span>
                    <div className="min-w-0 flex-1">
                      <div className="font-black text-xs truncate font-heading">{skill.name}</div>
                      <div className="text-[10px] text-muted-foreground">
                        x{skill.multiplier} DPS
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </Card>

          {/* Spirit Companion Selector */}
          <Card className="p-6 border border-border/10 glass-card rounded-3xl space-y-4 shadow-lg">
            <div className="flex items-center gap-2">
              <Sparkles className="size-5 text-emerald-400" />
              <h3 className="text-sm font-black uppercase font-heading tracking-wide">
                Дух-Спутник (Spirit)
              </h3>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {AVAILABLE_SPIRITS.map((spirit) => {
                const active = selectedSpirit === spirit.id
                return (
                  <div
                    key={spirit.id}
                    onClick={() => {
                      haptic.light()
                      setSelectedSpirit(spirit.id)
                    }}
                    className={`p-3 rounded-2xl border cursor-pointer transition-all text-center space-y-1 ${
                      active
                        ? 'bg-emerald-500/20 border-emerald-500 text-foreground shadow-md'
                        : 'bg-background/40 border-border/10 text-muted-foreground hover:bg-muted/30'
                    }`}
                  >
                    <div className="text-2xl">{spirit.icon}</div>
                    <div className="font-bold text-xs">{spirit.name}</div>
                    <div className="text-[9px] font-bold text-emerald-400">{spirit.bonus}</div>
                  </div>
                )
              })}
            </div>
          </Card>
        </div>

        {/* Right Stats & Output Summary */}
        <div className="xl:col-span-5 space-y-6">
          <Card className="p-8 border border-primary/20 glass-card rounded-3xl space-y-6 shadow-2xl relative overflow-hidden bg-gradient-to-br from-card via-primary/5 to-transparent">
            <div className="flex items-center justify-between border-b border-border/10 pb-4">
              <div className="flex items-center gap-2">
                <Zap className="size-5 text-primary animate-pulse" />
                <h3 className="text-base font-black uppercase font-heading">
                  Расчётные Характеристики
                </h3>
              </div>
              <Badge className="bg-emerald-500/20 text-emerald-400 border-0 text-[10px] font-black">
                READY
              </Badge>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-background/60 border border-border/10 flex justify-between items-center">
                <span className="text-xs font-bold text-muted-foreground uppercase">
                  Расчётный DPS Билда
                </span>
                <span className="text-2xl font-black text-primary font-heading">
                  {calculatedStats.totalDPS.toLocaleString()}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3.5 rounded-2xl bg-background/40 border border-border/10 space-y-1">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase">
                    Базовая Атака
                  </span>
                  <div className="text-base font-black font-heading">{calculatedStats.baseAtk}</div>
                </div>

                <div className="p-3.5 rounded-2xl bg-background/40 border border-border/10 space-y-1">
                  <span className="text-[10px] font-bold text-muted-foreground uppercase">
                    Бонус Промоута
                  </span>
                  <div className="text-base font-black text-emerald-400 font-heading">
                    +{calculatedStats.rankBonus}%
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-border/10">
              <Button
                variant="outline"
                className="w-full h-11 rounded-2xl font-bold text-xs uppercase tracking-wider gap-2 border-primary/30 text-primary hover:bg-primary/10 cursor-pointer"
                onClick={handleShare}
              >
                <Copy className="size-4" /> Поделиться конфигурацией
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
