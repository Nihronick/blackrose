export function CardIcon({ url, size = 48, placeholder = '📁' }) {
  return (
    <div className="card-icon" style={{ width: size, height: size }}>
      {url
        ? <img src={url} alt="" width={size * 0.72} height={size * 0.72} onError={e => e.target.style.display='none'} />
        : <span className="card-icon-placeholder">{placeholder}</span>
      }
    </div>
  )
}
