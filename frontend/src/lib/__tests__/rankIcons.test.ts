import { describe, it, expect } from 'vitest'
import { getRankIcon, getRankName, MAX_RANK, MIN_RANK, RANK_PROMOTIONS } from '../rankIcons'

describe('rankIcons utility', () => {
  it('should have 26 rank promotion entries', () => {
    expect(Object.keys(RANK_PROMOTIONS).length).toBe(26)
    expect(MIN_RANK).toBe(1)
    expect(MAX_RANK).toBe(26)
  })

  it('should map rank 1 to Stone', () => {
    expect(getRankName(1)).toBe('Stone')
    expect(getRankIcon(1)).toContain('Stone.png')
  })

  it('should map rank 26 to Auroite', () => {
    expect(getRankName(26)).toBe('Auroite')
    expect(getRankIcon(26)).toContain('Ether.png')
  })

  it('should fallback to Stone for unknown ranks', () => {
    expect(getRankName(999)).toBe('Rank 999')
    expect(getRankIcon(999)).toContain('Stone.png')
  })
})
