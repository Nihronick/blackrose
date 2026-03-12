const tg = window.Telegram?.WebApp

export const haptic = {
  light()   { tg?.HapticFeedback?.impactOccurred('light');   navigator.vibrate?.(10) },
  medium()  { tg?.HapticFeedback?.impactOccurred('medium');  navigator.vibrate?.(25) },
  heavy()   { tg?.HapticFeedback?.impactOccurred('heavy');   navigator.vibrate?.(40) },
  success() { tg?.HapticFeedback?.notificationOccurred('success') },
  error()   { tg?.HapticFeedback?.notificationOccurred('error') },
  select()  { tg?.HapticFeedback?.selectionChanged() },
}
