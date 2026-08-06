import { describe, it, expect } from 'vitest'
import { getRankIcon, getRankName, MAX_RANK, MIN_RANK, RANK_PROMOTIONS } from '../rankIcons'

describe('rankIcons utility', () => {
  it('should have 21 rank promotion entries', () => {
    expect(Object.keys(RANK_PROMOTIONS).length).toBe(21)
    expect(MIN_RANK).toBe(1)
    expect(MAX_RANK).toBe(21)
  })

  it('should map rank 1 to Stone', () => {
    expect(getRankName(1)).toBe('Stone')
    expect(getRankIcon(1)).toContain('Stone.png')
  })

  it('should map rank 21 to Infinaut', () => {
    expect(getRankName(21)).toBe('Infinaut')
    expect(getRankIcon(21)).toContain('Infinaut.png')
  })

  it('should fallback to Stone for unknown ranks', () => {
    expect(getRankName(999)).toBe('Rank 999')
    expect(getRankIcon(999)).toContain('Stone.png')
  })
})
