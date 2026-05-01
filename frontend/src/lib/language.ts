import type { AppLanguage } from '@/store'

const RU_PREFIX = 'ru_'

export const getLanguagePrefix = (language: AppLanguage) => (language === 'ru' ? RU_PREFIX : '')

export const isLanguageKey = (key: string, language: AppLanguage) =>
  language === 'ru' ? key.startsWith(RU_PREFIX) : !key.startsWith(RU_PREFIX)

export const applyLanguageKey = (key: string, language: AppLanguage) => {
  if (!key) return key
  if (language === 'ru') {
    return key.startsWith(RU_PREFIX) ? key : `${RU_PREFIX}${key}`
  }
  return key.startsWith(RU_PREFIX) ? key.slice(RU_PREFIX.length) : key
}
