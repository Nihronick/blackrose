import { hapticLight, hapticMedium } from '../lib/capacitor'
import { hapticImpact, hapticNotification, hapticSelection } from './telegram'

export const haptic = {
  light: () => {
    hapticLight().catch(() => {})
    hapticImpact('light')
  },
  medium: () => {
    hapticMedium().catch(() => {})
    hapticImpact('medium')
  },
  success: () => {
    hapticMedium().catch(() => {})
    hapticNotification('success')
  },
  select: () => {
    hapticLight().catch(() => {})
    hapticImpact('soft')
  },
  selection: () => {
    hapticLight().catch(() => {})
    hapticSelection()
  },
  heavy: () => {
    hapticMedium().catch(() => {})
    hapticImpact('heavy')
  },
  error: () => {
    hapticMedium().catch(() => {})
    hapticNotification('error')
  },
}
