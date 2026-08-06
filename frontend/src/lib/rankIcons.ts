import { GAME_ICONS } from './gameIcons'

export const RANK_PROMOTIONS: Record<number, { key: string; name: string }> = {
  1:  { key: 'stone', name: 'Stone' },
  2:  { key: 'bronze', name: 'Bronze' },
  3:  { key: 'iron', name: 'Iron' },
  4:  { key: 'silver', name: 'Silver' },
  5:  { key: 'eisenhart', name: 'Eisenhart' },
  6:  { key: 'eldenwood', name: 'Eldenwood' },
  7:  { key: 'adamant', name: 'Adamant' },
  8:  { key: 'orichalcum', name: 'Orichalcum' },
  9:  { key: 'blue_abyss', name: 'Blue Abyss' },
  10: { key: 'warfrost', name: 'Warfrost' },
  11: { key: 'diadust', name: 'Diadust' },
  12: { key: 'black_mythril', name: 'Black Mythril' },
  13: { key: 'dark_nox', name: 'Dark Nox' },
  14: { key: 'demon_metal', name: 'Demon Metal' },
  15: { key: 'ancient_canine', name: 'Ancient Canine' },
  16: { key: 'gigarock', name: 'Gigarock' },
  17: { key: 'cyclos', name: 'Cyclos' },
  18: { key: 'dragonos', name: 'Dragonos' },
  19: { key: 'ragnablood', name: 'Ragnablood' },
  20: { key: 'ether', name: 'Ether' },
  21: { key: 'infinaut', name: 'Infinaut' },
}

export function getRankIcon(rank: number): string {
  const entry = RANK_PROMOTIONS[rank]
  return entry ? (GAME_ICONS[entry.key] ?? '') : (GAME_ICONS['stone'] ?? '')
}

export function getRankName(rank: number): string {
  return RANK_PROMOTIONS[rank]?.name ?? `Rank ${rank}`
}

export const MAX_RANK = 21
export const MIN_RANK = 1
