import { describe, expect, it } from 'vitest'
import { formatGuideText } from '../markdown'
import { indexGuides, searchGuidesClient } from '../searchIndex'

describe('Markdown Enhanced Features', () => {
  it('renders interactive tabs correctly', () => {
    const raw = `:::tabs
== Ранняя игра
Советы для новичков
== Поздняя игра
Советы для лейтгейма
:::`
    const html = formatGuideText(raw)
    expect(html).toContain('class="guide-tabs"')
    expect(html).toContain('guide-tab-btn active')
    expect(html).toContain('Ранняя игра')
    expect(html).toContain('Поздняя игра')
    expect(html).toContain('class="guide-tab-panel hidden"')
  })

  it('renders callout blocks correctly', () => {
    const raw = `:::tip
Повышайте уровень Саламандры для максимального DPS!
:::`
    const html = formatGuideText(raw)
    expect(html).toContain('guide-callout guide-callout-tip')
    expect(html).toContain('💡')
    expect(html).toContain('Повышайте уровень Саламандры')
  })
})

describe('MiniSearch Client Index', () => {
  it('indexes and finds guides with fuzzy matching', () => {
    indexGuides([
      {
        key: 'guide_blitz_gold',
        title: 'Блиц Голд и Фарм Золота',
        preview: 'Оптимальный сетап для фарма',
        category_key: 'stage',
      },
      {
        key: 'guide_spirits_build',
        title: 'Духи и Синергии',
        preview: 'Ной Саламандра и Лой',
        category_key: 'spirit',
      },
    ])

    const results = searchGuidesClient('Блиц')
    expect(results.length).toBeGreaterThan(0)
    expect(results[0].key).toBe('guide_blitz_gold')

    const spiritResults = searchGuidesClient('Духи')
    expect(spiritResults.length).toBeGreaterThan(0)
    expect(spiritResults[0].key).toBe('guide_spirits_build')
  })
})
