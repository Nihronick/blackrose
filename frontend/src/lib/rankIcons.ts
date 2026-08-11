import { GAME_ICONS } from './gameIcons'

export const RANK_PROMOTIONS: Record<number, { key: string; name: string }> = {
  1: { key: 'stone', name: 'Stone' },
  2: { key: 'bronze', name: 'Bronze' },
  3: { key: 'iron', name: 'Iron' },
  4: { key: 'silver', name: 'Silver' },
  5: { key: 'promotion_gold', name: 'Gold' },
  6: { key: 'mithril', name: 'Mithril' },
  7: { key: 'orichalcum', name: 'Orichalcum' },
  8: { key: 'arcanite', name: 'Arcanite' },
  9: { key: 'adamant', name: 'Adamant' },
  10: { key: 'ether', name: 'Ether' },
  11: { key: 'black_mythril', name: 'Black Mythril' },
  12: { key: 'demon_metal', name: 'Demon Metal' },
  13: { key: 'dragonos', name: 'Dragonos' },
  14: { key: 'ragnablood', name: 'Ragnablood' },
  15: { key: 'warfrost', name: 'Warfrost' },
  16: { key: 'dark_nox', name: 'Dark Nox' },
  17: { key: 'blue_abyss', name: 'Blue Abyss' },
  18: { key: 'infinaut', name: 'Infinaut' },
  19: { key: 'cyclos', name: 'Cyclos' },
  20: { key: 'ancient_canine', name: 'Ancient Canine' },
  21: { key: 'gigarock', name: 'Gigarock' },
  22: { key: 'eisenhart', name: 'Eisenhart' },
  23: { key: 'diadust', name: 'Diadust' },
  24: { key: 'eldenwood', name: 'Eldenwood' },
  25: { key: 'blitz_gold', name: 'Blitz Gold' },
  26: { key: 'auroite', name: 'Auroite' },
}

export function getRankIcon(rank: number): string {
  const entry = RANK_PROMOTIONS[rank]
  return entry ? (GAME_ICONS[entry.key] ?? '') : (GAME_ICONS.stone ?? '')
}

export function getRankName(rank: number): string {
  return RANK_PROMOTIONS[rank]?.name ?? `Rank ${rank}`
}

export const MAX_RANK = 26
export const MIN_RANK = 1
