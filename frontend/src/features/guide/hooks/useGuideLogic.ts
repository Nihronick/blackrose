import { getGameIconUrl } from '@/lib/gameIcons'
import { formatGuideText } from '@/lib/markdown'
import type { Guide } from '@/lib/types'
import { normalizeUrl } from '@/lib/utils'
import { useMemo } from 'react'

export function useGuideLogic(guide: Guide | undefined) {
  const formattedText = useMemo(() => {
    const rawText = guide?.text || guide?.text_content || ''
    if (!rawText) return ''

    return formatGuideText(rawText, {
      guideLinks: (guide?.guide_links as Record<string, { title?: string; icon?: string }>) ?? {},
      iconResolver: (nameValue: string) => {
        const name = nameValue?.trim()
        if (!name) return ''

        // 1. Direct match in guide.icons
        if (guide?.icons && guide.icons[name]) return normalizeUrl(guide.icons[name])

        // 2. Fuzzy match in guide.icons
        if (guide?.icons) {
          const normalize = (s: string) => s.toLowerCase().replace(/_/g, '').replace(/s$/, '')
          const searchName = normalize(name)

          for (const key in guide.icons) {
            if (normalize(key) === searchName) {
              return normalizeUrl(guide.icons[key])
            }
          }
        }

        // 3. Fallback to GAME_ICONS registry!
        const globalIcon = getGameIconUrl(name)
        if (globalIcon) return normalizeUrl(globalIcon)

        return ''
      },
    })
  }, [guide])

  return { formattedText }
}
