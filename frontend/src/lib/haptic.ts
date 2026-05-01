import { hapticLight, hapticMedium } from '../lib/capacitor'

export const haptic = {
  light: () => {
    hapticLight().catch(() => {})
  },
  medium: () => {
    hapticMedium().catch(() => {})
  },
  success: () => {
    hapticMedium().catch(() => {})
  },
  select: () => {
    hapticLight().catch(() => {})
  },
  heavy: () => {
    hapticMedium().catch(() => {})
  },
  error: () => {
    hapticMedium().catch(() => {})
  },
}
