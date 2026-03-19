import { haptic } from '../haptic'
import { CardIcon } from '../components/CardIcon'

export function HistoryView({ history, onSelectGuide }) {
  if (!history || history.length === 0) {
    return (
      <div className="view-scroll">
        <div className="fav-empty">
          <div className="fav-empty-icon">🕐</div>
          <h3>История пуста</h3>
          <p>Здесь появятся гайды, которые вы недавно открывали</p>
        </div>
      </div>
    )
  }

  return (
    <div className="view-scroll">
      <div className="list">
        {history.map((item, idx) => (
          <div key={`${item.key}-${idx}`} className="card"
            onClick={() => { haptic.light(); onSelectGuide(item.key, item.title, item.icon) }}>
            <CardIcon url={item.icon} placeholder="📖" />
            <div className="card-body">
              <div className="card-title">{item.title || item.key}</div>
              <div className="card-subtitle" style={{marginTop:'2px'}}>
                {idx === 0 ? 'Только что' : `#${idx + 1}`}
              </div>
            </div>
            <span className="card-arrow">›</span>
          </div>
        ))}
      </div>
    </div>
  )
}
