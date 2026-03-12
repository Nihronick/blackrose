import { haptic } from '../haptic'

export function QuickNav({ categories, onSelect, onHome, onClose }) {
  return (
    <>
      <div className="qn-overlay" onClick={onClose} />
      <div className="qn-popup">
        <div className="qn-label">Перейти в раздел</div>
        {categories.map(cat => (
          <div key={cat.key} className="qn-item" onClick={() => { haptic.select(); onSelect(cat) }}>
            <div className="qn-icon">
              {cat.icon
                ? <img src={cat.icon} alt="" width={28} height={28} onError={e => e.target.style.display='none'} />
                : <span>📁</span>
              }
            </div>
            <span className="qn-title">{cat.title}</span>
          </div>
        ))}
        <div className="qn-divider" />
        <div className="qn-item" onClick={() => { haptic.select(); onHome() }}>
          <div className="qn-icon qn-icon-home">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--accent-text)">
              <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
            </svg>
          </div>
          <span className="qn-title">Главное меню</span>
        </div>
      </div>
    </>
  )
}
