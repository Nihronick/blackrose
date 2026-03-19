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

function CyberlinkPopup({ guideKey, title, icon, onOpen, onClose }) {
  const [loading, setLoading] = useState(false)
  const [preview, setPreview] = useState(null)

  useEffect(() => {
    setLoading(true)
    apiFetch(`/api/guide/${guideKey}`)
      .then(res => setPreview(res))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [guideKey])

  return (
    <div className="cyberlink-popup-overlay" onClick={onClose}>
      <div className="cyberlink-popup" onClick={e => e.stopPropagation()}>
        <div className="cyberlink-popup-header">
          {icon && <img src={icon} alt="" width={28} height={28} className="cyberlink-popup-icon"
            onError={e => e.target.style.display='none'}/>}
          <span className="cyberlink-popup-title">{title}</span>
          <button className="cyberlink-popup-close" onClick={onClose}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="16" height="16">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div className="cyberlink-popup-body">
          {loading && <div className="cyberlink-popup-loading"><div className="cyberlink-spinner"/></div>}
          {!loading && preview && (
            <div className="cyberlink-popup-text guide-content"
              dangerouslySetInnerHTML={{ __html: preview.text }}/>
          )}
          {!loading && !preview && <div className="cyberlink-popup-error">Не удалось загрузить гайд</div>}
        </div>
        <div className="cyberlink-popup-footer">
          <button className="cyberlink-open-btn" onClick={() => { onOpen(guideKey, preview?.title, preview?.icon); onClose() }}>
            Открыть гайд
            <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M3 8h10M9 4l4 4-4 4"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export function GuideView({ guideKey, isFavorite, onToggleFavorite, onOpenGuide, onGuideLoaded }) {
  const [guide, setGuide]         = useState(null)
  const [error, setError]         = useState(null)
  const [lightbox, setLightbox]   = useState(null)
  const [cyberlink, setCyberlink] = useState(null)
  const scrollRef  = useRef(null)
  const contentRef = useRef(null)

  const load = useCallback(async () => {
    try {
      const res = await apiFetch(`/api/guide/${guideKey}`)
      setGuide(res)
      setError(null)
      onGuideLoaded?.(res)   // ← notify App to add to history with full title+icon
    } catch (e) {
      if (e.message !== 'ACCESS_DENIED') setError(e.message)
    }
  }, [guideKey, onGuideLoaded])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    const el = contentRef.current
    if (!el) return
    const handleClick = (e) => {
      const link = e.target.closest('a[data-guide-key]')
      if (!link) return
      e.preventDefault()
      haptic.light()
      setCyberlink({
        key:   link.dataset.guideKey,
        title: link.dataset.guideTitle || link.dataset.guideKey,
        icon:  link.dataset.guideIcon  || '',
      })
    }
    el.addEventListener('click', handleClick)
    return () => el.removeEventListener('click', handleClick)
  }, [guide])

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

            <div ref={contentRef} className="guide-content"
              dangerouslySetInnerHTML={{ __html: guide.text }}/>

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

      {cyberlink && (
        <CyberlinkPopup
          guideKey={cyberlink.key}
          title={cyberlink.title}
          icon={cyberlink.icon}
          onOpen={onOpenGuide}
          onClose={() => setCyberlink(null)}
        />
      )}
    </>
  )
}
