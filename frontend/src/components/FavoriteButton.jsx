import { haptic } from '../haptic'

export function FavoriteButton({ isFav, onToggle, size = 28 }) {
  const handle = (e) => {
    e.stopPropagation()
    haptic.success()
    onToggle()
  }

  return (
    <button
      className={`fav-btn${isFav ? ' fav-btn-active' : ''}`}
      onClick={handle}
      style={{ width: size, height: size }}
      title={isFav ? 'Убрать из избранного' : 'В избранное'}
    >
      <svg viewBox="0 0 24 24" width={size * 0.65} height={size * 0.65}
        fill={isFav ? 'currentColor' : 'none'}
        stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
    </button>
  )
}
