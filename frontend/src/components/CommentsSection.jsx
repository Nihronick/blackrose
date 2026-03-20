import { useState, useEffect, useRef } from 'react'
import { apiGetComments, apiAddComment, apiDeleteComment } from '../api'
import { haptic } from '../haptic'

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return 'только что'
  if (diff < 3600) return `${Math.floor(diff / 60)} мин назад`
  if (diff < 86400) return `${Math.floor(diff / 3600)} ч назад`
  return d.toLocaleDateString('ru', { day: 'numeric', month: 'short' })
}

const TRASH_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14">
    <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/>
    <path d="M10 11v6M14 11v6M9 6V4h6v2"/>
  </svg>
)

export function CommentsSection({ guideKey }) {
  const [comments, setComments] = useState([])
  const [loading, setLoading]   = useState(true)
  const [text, setText]         = useState('')
  const [sending, setSending]   = useState(false)
  const [open, setOpen]         = useState(false)
  const inputRef = useRef(null)

  const load = async () => {
    try {
      const res = await apiGetComments(guideKey)
      setComments(res.comments || [])
    } catch {}
    finally { setLoading(false) }
  }

  useEffect(() => { if (open) load() }, [open, guideKey])

  const send = async () => {
    if (!text.trim() || sending) return
    setSending(true)
    haptic.light()
    try {
      await apiAddComment(guideKey, text.trim())
      setText('')
      await load()
      haptic.success()
    } catch (e) {
      haptic.error?.()
    } finally { setSending(false) }
  }

  const remove = async (id) => {
    haptic.light()
    try {
      await apiDeleteComment(guideKey, id)
      setComments(c => c.filter(x => x.id !== id))
    } catch {}
  }

  return (
    <div className="comments-section">
      <button className="comments-toggle" onClick={() => { haptic.light(); setOpen(o => !o) }}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="16" height="16">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
        </svg>
        <span>Комментарии</span>
        {comments.length > 0 && <span className="comments-count">{comments.length}</span>}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"
          style={{ marginLeft: 'auto', transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }}>
          <path d="M6 9l6 6 6-6"/>
        </svg>
      </button>

      {open && (
        <div className="comments-body">
          {loading && <div className="comments-loading"><div className="adm2-spinner"/></div>}
          {!loading && comments.length === 0 && (
            <div className="comments-empty">Комментариев пока нет. Будьте первым!</div>
          )}
          {!loading && comments.map(c => (
            <div key={c.id} className={`comment-item${c.is_own ? ' own' : ''}`}>
              <div className="comment-meta">
                <span className="comment-name">{c.name}</span>
                <span className="comment-time">{formatTime(c.created_at)}</span>
                {c.is_own && (
                  <button className="comment-delete" onClick={() => remove(c.id)}>{TRASH_ICON}</button>
                )}
              </div>
              <div className="comment-text">{c.text}</div>
            </div>
          ))}

          <div className="comments-input-row">
            <input
              ref={inputRef}
              className="comments-input"
              placeholder="Написать комментарий..."
              value={text}
              onChange={e => setText(e.target.value)}
              maxLength={1000}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
            />
            <button className="comments-send" onClick={send} disabled={!text.trim() || sending}>
              {sending
                ? <div className="adm2-spinner adm2-spinner-sm"/>
                : <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M2 21l21-9L2 3v7l15 2-15 2v7z"/></svg>
              }
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
