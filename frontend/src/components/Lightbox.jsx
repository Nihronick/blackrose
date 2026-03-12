import { useEffect } from 'react'

export function Lightbox({ src, onClose }) {
  useEffect(() => {
    const fn = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', fn)
    return () => window.removeEventListener('keydown', fn)
  }, [onClose])

  return (
    <div className="lightbox" onClick={e => { if (e.target === e.currentTarget) onClose() }}>
      <button className="lightbox-close" onClick={onClose}>✕</button>
      <img src={src} alt="" />
    </div>
  )
}
