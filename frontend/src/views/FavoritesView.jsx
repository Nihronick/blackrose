import { haptic } from '../haptic'
import { CardIcon } from '../components/CardIcon'
import { FavoriteButton } from '../components/FavoriteButton'

export function FavoritesView({ favorites, onSelectGuide, onToggle }) {
  if (favorites.length === 0) {
    return (
      <div className="view-scroll">
        <div className="fav-empty">
          <div className="fav-empty-icon">⭐</div>
          <h3>Избранное пусто</h3>
          <p>Нажмите ⭐ на любом гайде чтобы сохранить его здесь</p>
        </div>
      </div>
    )
  }

  return (
    <div className="view-scroll">
      <div className="list">
        {favorites.map(item => (
          <div key={item.key} className="card"
            onClick={() => { haptic.light(); onSelectGuide(item.key) }}>
            <CardIcon url={item.icon} placeholder="📖" />
            <div className="card-body">
              <div className="card-title">{item.title}</div>
            </div>
            <FavoriteButton isFav={true} onToggle={() => onToggle(item)} />
          </div>
        ))}
      </div>
    </div>
  )
}
