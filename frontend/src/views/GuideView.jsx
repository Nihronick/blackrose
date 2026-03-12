import { useState, useEffect, useRef, useCallback } from 'react'
import { apiFetch } from '../api'
import { haptic } from '../haptic'
import { parseVideo, parseDocument } from '../utils'
import { SkeletonGuide } from '../components/Skeleton'
import { Lightbox } from '../components/Lightbox'
import { FavoriteButton } from '../components/FavoriteButton'
import { PtrIndicator } from '../components/PtrIndicator'
import { usePullToRefresh } from '../hooks/usePullToRefresh'

function VideoBlock({ url }) {
  const v = parseVideo(url)
  if (!v) return null
  if (v.type === 'youtube')
    return <div className="video-wrapper"><iframe src={`https://www.youtube.com/embed/${v.id}`} allowFullScreen title="video"/></div>
  if (v.type === 'video')
    return <div className="video-wrapper"><video controls preload="metadata" playsInline><source src={url}/></video></div>
  return (
    <a href={url} target="_blank" rel="noreferrer" className="doc-link">
      <span className="doc-icon">🎬</span>
      <div><div className="doc-name">Видео</div><div className="doc-hint">Открыть</div></div>
    </a>
  )
}

function DocBlock({ url }) {
  const d = parseDocument(url)
  if (!d) return null
  return (
    <a href={d.url} target="_blank" rel="noreferrer" className="doc-link">
      <span className="doc-icon">{d.icon}</span>
      <div><div className="doc-name">{d.name}</div><div className="doc-hint">Скачать · {d.ext.toUpperCase()}</div></div>
    </a>
  )
}

export function GuideView({ guideKey, isFavorite, onToggleFavorite }) {
  const [guide, setGuide]       = useState(null)
  const [error, setError]       = useState(null)
  const [lightbox, setLightbox] = useState(null)
  const scrollRef = useRef(null)

  const load = useCallback(async () => {
    try {
      const res = await apiFetch(`/api/guide/${guideKey}`)
      setGuide(res); setError(null)
    } catch (e) {
      if (e.message !== 'ACCESS_DENIED') setError(e.message)
    }
  }, [guideKey])

  useEffect(() => { load() }, [load])

  const { pullY, refreshing } = usePullToRefresh(scrollRef, load)

  return (
    <>
      <div className="view-scroll" ref={scrollRef}>
        <PtrIndicator pullY={pullY} refreshing={refreshing} />
        {error && <div className="guide-wrap"><div className="state-error">{error}</div></div>}
        {!error && !guide && <SkeletonGuide />}
        {!error && guide && (
          <div className="guide-wrap">
            <div className="guide-header">
              <div className="guide-icon-box">
                {guide.icon && <img src={guide.icon} alt="" onError={e => e.target.style.display='none'} />}
              </div>
              <h2 className="guide-title">{guide.title}</h2>
              <FavoriteButton
                isFav={isFavorite}
                onToggle={() => onToggleFavorite({ key: guide.key, title: guide.title, icon: guide.icon })}
                size={36}
              />
            </div>
            <div className="guide-content" dangerouslySetInnerHTML={{ __html: guide.text }} />
            {(guide.photo || []).filter(s => s && !s.startsWith('Ag')).map((src, i) => (
              <img key={i} src={src} className="guide-photo" loading="lazy" alt=""
                onError={e => e.target.style.display='none'}
                onClick={() => { haptic.light(); setLightbox(src) }} />
            ))}
            {(guide.video    || []).map((url, i) => <VideoBlock key={i} url={url} />)}
            {(guide.document || []).map((url, i) => <DocBlock   key={i} url={url} />)}
          </div>
        )}
      </div>
      {lightbox && <Lightbox src={lightbox} onClose={() => setLightbox(null)} />}
    </>
  )
}
