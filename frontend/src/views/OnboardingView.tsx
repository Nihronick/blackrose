import { haptic } from '@/lib/haptic'
import { ChevronRight, Compass, Globe, Hammer, Moon, Shield, Sparkles, Sun } from '@/lib/icons'
import { useAppStore } from '@/store'
import { AnimatePresence, motion } from 'framer-motion'
import { useState } from 'react'

export const OnboardingView = () => {
  const { theme, setTheme, language, setLanguage, completeOnboarding } = useAppStore()
  const [step, setStep] = useState(1)

  const nextStep = () => {
    haptic.medium()
    setStep((s) => Math.min(s + 1, 3))
  }

  const prevStep = () => {
    haptic.light()
    setStep((s) => Math.max(s - 1, 1))
  }

  const variants = {
    initial: (direction: number) => ({
      x: direction > 0 ? 100 : -100,
      opacity: 0,
    }),
    animate: {
      x: 0,
      opacity: 1,
      transition: { duration: 0.4, ease: 'easeOut' as const },
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 100 : -100,
      opacity: 0,
      transition: { duration: 0.3, ease: 'easeOut' as const },
    }),
  }

  // Define steps
  return (
    <div className="fixed inset-0 z-50 bg-background flex flex-col overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden mesh-bg opacity-50">
        <div className="absolute -top-[20%] -left-[10%] w-[70%] h-[50%] bg-primary/20 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute -bottom-[20%] -right-[10%] w-[60%] h-[60%] bg-violet-500/10 blur-[100px] rounded-full" />
      </div>

      <div className="relative z-10 flex-1 flex flex-col">
        {/* Progress bar */}
        <div className="h-1 w-full bg-muted/30">
          <motion.div
            className="h-full bg-gradient-to-r from-primary to-violet-500"
            initial={{ width: '33%' }}
            animate={{ width: `${(step / 3) * 100}%` }}
            transition={{ duration: 0.5, ease: 'easeInOut' as const }}
          />
        </div>

        {/* Content Area */}
        <div className="flex-1 relative">
          <AnimatePresence mode="wait" custom={1}>
            {step === 1 && (
              <motion.div
                key="step1"
                custom={1}
                variants={variants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center"
              >
                <div className="size-32 rounded-[40px] bg-gradient-to-br from-primary/20 to-violet-500/10 border border-primary/20 flex items-center justify-center mb-8 shadow-glow ambient-glow">
                  <div className="size-20 rounded-[28px] bg-background shadow-xl flex items-center justify-center border-4 border-background">
                    <span className="text-4xl font-black text-foreground">B</span>
                  </div>
                </div>
                <h1 className="text-3xl sm:text-4xl font-black font-heading mb-4 tracking-tight">
                  Добро пожаловать в{' '}
                  <span className="bg-gradient-to-r from-primary to-violet-400 bg-clip-text text-transparent">
                    BlackRose
                  </span>
                </h1>
                <p className="text-muted-foreground font-medium leading-relaxed max-w-sm">
                  Ваш персональный карманный компаньон, база знаний и набор инструментов для
                  комфортной игры.
                </p>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div
                key="step3"
                custom={1}
                variants={variants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="absolute inset-0 flex flex-col p-6 pt-12"
              >
                <h2 className="text-2xl font-black font-heading mb-2">Настройки комфорта</h2>
                <p className="text-sm text-muted-foreground font-medium mb-8">
                  Настрой внешний вид и язык базы знаний.
                </p>

                <div className="flex flex-col gap-6">
                  {/* Theme Selection */}
                  <div className="flex flex-col gap-3">
                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground font-heading">
                      Тема оформления
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => {
                          haptic.light()
                          setTheme('dark')
                        }}
                        className={`p-4 rounded-[24px] border flex flex-col items-center gap-3 transition-all ${theme === 'dark' ? 'bg-primary/10 border-primary shadow-glow' : 'bg-muted/30 border-border/10'}`}
                      >
                        <div className="size-12 rounded-2xl bg-slate-900 flex items-center justify-center border border-white/10 shadow-inner">
                          <Moon className="size-6 text-primary" />
                        </div>
                        <span className="text-sm font-bold font-heading">Темная</span>
                      </button>
                      <button
                        onClick={() => {
                          haptic.light()
                          setTheme('light')
                        }}
                        className={`p-4 rounded-[24px] border flex flex-col items-center gap-3 transition-all ${theme === 'light' ? 'bg-primary/10 border-primary shadow-glow' : 'bg-muted/30 border-border/10'}`}
                      >
                        <div className="size-12 rounded-2xl bg-white flex items-center justify-center border border-black/10 shadow-sm">
                          <Sun className="size-6 text-amber-500" />
                        </div>
                        <span className="text-sm font-bold font-heading">Светлая</span>
                      </button>
                    </div>
                  </div>

                  {/* Language Selection */}
                  <div className="flex flex-col gap-3 mt-4">
                    <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground font-heading">
                      Язык гайдов
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => {
                          haptic.light()
                          setLanguage('ru')
                        }}
                        className={`p-4 rounded-[24px] border flex items-center gap-3 transition-all ${language === 'ru' ? 'bg-primary/10 border-primary shadow-glow' : 'bg-muted/30 border-border/10'}`}
                      >
                        <span className="text-2xl drop-shadow-sm">🇷🇺</span>
                        <span className="text-sm font-bold font-heading">Русский</span>
                      </button>
                      <button
                        onClick={() => {
                          haptic.light()
                          setLanguage('en')
                        }}
                        className={`p-4 rounded-[24px] border flex items-center gap-3 transition-all ${language === 'en' ? 'bg-primary/10 border-primary shadow-glow' : 'bg-muted/30 border-border/10'}`}
                      >
                        <span className="text-2xl drop-shadow-sm">🇬🇧</span>
                        <span className="text-sm font-bold font-heading">English</span>
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div
                key="step4"
                custom={1}
                variants={variants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center"
              >
                <div className="size-24 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center mb-6 shadow-glow border border-emerald-500/30">
                  <Sparkles className="size-10" />
                </div>
                <h2 className="text-3xl font-black font-heading mb-4">Всё готово!</h2>
                <p className="text-muted-foreground font-medium leading-relaxed max-w-xs">
                  Приложение настроено и готово к использованию. Приятной игры!
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Bottom Navigation / CTA */}
        <div className="p-6 pb-8 flex items-center justify-between border-t border-border/5 bg-background/50 backdrop-blur-lg">
          {step > 1 ? (
            <button
              onClick={prevStep}
              className="px-6 py-4 font-bold text-muted-foreground hover:text-foreground transition-colors font-heading text-sm uppercase tracking-wider"
            >
              Назад
            </button>
          ) : (
            <div /> // Spacer
          )}

          {step < 3 ? (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                nextStep()
              }}
              className="flex items-center gap-2 bg-foreground text-background px-8 py-4 rounded-full font-black text-sm uppercase tracking-wider font-heading hover:opacity-90 transition-opacity shadow-lg"
            >
              Далее
              <ChevronRight className="size-4" />
            </motion.button>
          ) : (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                haptic.heavy()
                completeOnboarding()
              }}
              className="flex items-center justify-center w-full bg-gradient-to-r from-primary to-violet-500 text-white px-8 py-4 rounded-full font-black text-sm uppercase tracking-widest font-heading shadow-glow border border-white/10"
            >
              Начать использование
            </motion.button>
          )}
        </div>
      </div>
    </div>
  )
}
