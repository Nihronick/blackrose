import { useState, useEffect, useRef, useCallback } from 'react'
import { apiFetch, apiRecordView } from '../api'
import { haptic } from '../haptic'
import { parseVideo, parseDocument } from '../utils'
import { SkeletonGuide } from '../components/Skeleton'
import { Lightbox } from '../components/Lightbox'
import { FavoriteButton } from '../components/FavoriteButton'
import { PtrIndicator } from '../components/PtrIndicator'
import { CommentsSection } from '../components/CommentsSection'
import { TagsList } from '../components/TagBadge'
import { usePullToRefresh } from '../hooks/usePullToRefresh'

const tgApp = window.Telegram?.WebApp

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

function ShareButton({ guide }) {
  const [shared, setShared] = useState(false)

  const share = () => {
    haptic.light()
    const botUsername = 'blackrosesl1_bot'
    const deepLink = `https://t.me/${botUsername}?start=guide_${guide.key}`

    // Try Telegram share first
    if (tgApp?.switchInlineQuery) {
      tgApp.switchInlineQuery(guide.title, ['users', 'groups'])
      return
    }
    // Fallback: copy deep link
    navigator.clipboard?.writeText(deepLink).then(() => {
      setShared(true)
      haptic.success?.()
      setTimeout(() => setShared(false), 2000)
    }).catch(() => {
      // last resort: open share
      if (navigator.share) {
        navigator.share({ title: guide.title, url: deepLink })
      }
    })
  }

  return (
    <button className="guide-share-btn" onClick={share} title="Поделиться">
      {shared
        ? <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" width="18" height="18"><path d="M20 6L9 17l-5-5"/></svg>
        : <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="18" height="18">
            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
            <polyline points="16 6 12 2 8 6"/>
            <line x1="12" y1="2" x2="12" y2="15"/>
          </svg>
      }
    </button>
  )
}

function ViewsCounter({ views }) {
  if (!views) return null
  return (
    <span className="guide-views">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="13" height="13">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
      {views >= 1000 ? `${(views / 1000).toFixed(1)}k` : views}
    </span>
  )
}

export function GuideView({ guideKey, isFavorite, onToggleFavorite, onOpenGuide, onGuideLoaded, onTagClick }) {
  const [guide, setGuide]         = useState(null)
  const [error, setError]         = useState(null)
  const [lightbox, setLightbox]   = useState(null)
  const [cyberlink, setCyberlink] = useState(null)
  const scrollRef  = useRef(null)
  const contentRef = useRef(null)
  const viewRecorded = useRef(false)

  const load = useCallback(async () => {
    try {
      const res = await apiFetch(`/api/guide/${guideKey}`)
      setGuide(res)
      setError(null)
      onGuideLoaded?.(res)
    } catch (e) {
      if (e.message !== 'ACCESS_DENIED') setError(e.message)
    }
  }, [guideKey, onGuideLoaded])

  useEffect(() => { load() }, [load])

  // Record view once per mount
  useEffect(() => {
    if (!guideKey || viewRecorded.current) return
    viewRecorded.current = true
    apiRecordView(guideKey).catch(() => {})
  }, [guideKey])

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
              <div className="guide-header-info">
                <h2 className="guide-title">{guide.title}</h2>
                <div className="guide-header-meta">
                  <ViewsCounter views={guide.views} />
                  {guide.tags?.length > 0 && (
                    <TagsList tags={guide.tags} onTagClick={onTagClick} />
                  )}
                </div>
              </div>
              <div className="guide-header-actions">
                <ShareButton guide={guide} />
                <FavoriteButton
                  isFav={isFavorite}
                  onToggle={() => onToggleFavorite({ key: guide.key, title: guide.title, icon: guide.icon })}
                  size={36}
                />
              </div>
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

            <CommentsSection guideKey={guideKey} />
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
