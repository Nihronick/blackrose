import { hapticLight, hapticMedium } from '../lib/capacitor'
import { hapticImpact, hapticNotification } from './telegram'

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
  heavy: () => {
    hapticMedium().catch(() => {})
    hapticImpact('heavy')
  },
  error: () => {
    hapticMedium().catch(() => {})
    hapticNotification('error')
  },
}
