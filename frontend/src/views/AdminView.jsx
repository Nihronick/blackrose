import { useState, useEffect, useCallback, useRef } from 'react'
import { ExportImport } from '../components/ExportImport'
import { ReorderList } from '../components/ReorderList'
import { apiReorderGuides, apiReorderCategories } from '../api'
import { apiFetch, apiPut, apiDelete, apiIconsGrouped } from '../api'
import { haptic } from '../haptic'
import { IconLibrary } from '../components/IconLibrary'

const adminFetch  = (path)       => apiFetch(path)
const adminPut    = (path, body) => apiPut(path, body)
const adminDelete = (path)       => apiDelete(path)

const IC = {
  back:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>,
  close: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="16" height="16"><path d="M18 6L6 18M6 6l12 12"/></svg>,
  edit:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="15" height="15"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  trash: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="15" height="15"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>,
  plus:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" width="16" height="16"><path d="M12 5v14M5 12h14"/></svg>,
  save:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="16" height="16"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>,
  bold:  <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>,
  italic:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" width="14" height="14"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>,
  under: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><path d="M6 3v7a6 6 0 0 0 6 6 6 6 0 0 0 6-6V3"/><line x1="4" y1="21" x2="20" y2="21"/></svg>,
  strike:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><line x1="5" y1="12" x2="19" y2="12"/><path d="M16 6C16 6 14.5 4 12 4C9.5 4 7 5.5 7 8C7 9.5 8 10.5 9.5 11"/><path d="M8 18C8 18 9.5 20 12 20C14.5 20 17 18.5 17 16C17 14.5 16 13.5 14.5 13"/></svg>,
  code:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>,
  link:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>,
  quote: <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>,
  ul:    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><line x1="9" y1="6" x2="20" y2="6"/><line x1="9" y1="12" x2="20" y2="12"/><line x1="9" y1="18" x2="20" y2="18"/><circle cx="4" cy="6" r="1.5" fill="currentColor" stroke="none"/><circle cx="4" cy="12" r="1.5" fill="currentColor" stroke="none"/><circle cx="4" cy="18" r="1.5" fill="currentColor" stroke="none"/></svg>,
  ol:    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><path d="M4 6h1v4M4 10h2M6 18H4c0-1 2-2 2-3s-1-1.5-2-1" stroke="currentColor"/></svg>,
  spoil: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>,
  srch:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>,
  cyber: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" width="14" height="14"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 17.5h3m0 0V14m0 3.5L21 21"/></svg>,
}

function IconPreview({ url }) {
  if (!url) return <div className="adm2-icon-empty">?</div>
  return <img src={url} alt="" width={34} height={34} className="adm2-icon-img"
    onError={e => { e.target.style.display='none' }} />
}

// ── Rich Text Toolbar ──────────────────────────────────
const TOOLBAR = [
  { divider: true },
  [
    { html: 'H2', title: 'Заголовок 2',    wrap: ['## ', ''] },
    { html: 'H3', title: 'Заголовок 3',    wrap: ['### ', ''] },
  ],
  { divider: true },
  [
    { icon: 'bold',   title: 'Жирный **B**',      wrap: ['**','**'] },
    { icon: 'italic', title: 'Курсив *I*',         wrap: ['*','*'] },
    { icon: 'under',  title: 'Подчёркнутый',      wrap: ['<u>','</u>'] },
    { icon: 'strike', title: 'Зачёркнутый ~~S~~',  wrap: ['~~','~~'] },
    { icon: 'spoil',  title: 'Спойлер ||text||',  wrap: ['||','||'] },
  ],
  { divider: true },
  [
    { icon: 'code',   title: 'Код `code`',         wrap: ['`','`'] },
    { icon: 'quote',  title: 'Цитата > …',         wrap: ['> ',''] },
    { icon: 'link',   title: 'Ссылка [text](url)', wrap: ['[','](url)'] },
  ],
  { divider: true },
  [
    { icon: 'ul', title: 'Маркированный список', prefix: '- ' },
    { icon: 'ol', title: 'Нумерованный список',  prefix: '1. ' },
  ],
  { divider: true },
  [
    { icon: 'cyber', title: 'Киберссылка на гайд [[key]] или [[key|Текст]]', wrap: ['[[', ']]'] },
  ],
]

function RichToolbar({ textareaRef, value, onChange }) {
  const apply = (item) => {
    const el = textareaRef.current
    if (!el) return
    const s = el.selectionStart, e = el.selectionEnd
    const sel = value.slice(s, e)
    let next, cur

    if (item.prefix) {
      const before = value.slice(0, s)
      const lineStart = before.lastIndexOf('\n') + 1
      const lines = value.slice(lineStart, e).split('\n')
      const rep = lines.map(l => item.prefix + l).join('\n')
      next = value.slice(0, lineStart) + rep + value.slice(e)
      cur = lineStart + rep.length
    } else {
      const [o, c] = item.wrap
      const ph = o.startsWith('#') ? 'Заголовок' : o === '> ' ? 'Текст цитаты' : 'текст'
      const ins = sel || ph
      next = value.slice(0, s) + o + ins + c + value.slice(e)
      cur = s + o.length + ins.length
    }

    onChange(next)
    requestAnimationFrame(() => { el.focus(); el.setSelectionRange(cur, cur) })
    haptic.light()
  }

  return (
    <div className="adm2-toolbar">
      {TOOLBAR.map((item, i) => {
        if (item.divider) return <div key={i} className="adm2-toolbar-div"/>
        return (
          <div key={i} className="adm2-toolbar-group">
            {item.map((btn, j) => (
              <button key={j} type="button" className="adm2-toolbar-btn"
                title={btn.title} onMouseDown={ev => { ev.preventDefault(); apply(btn) }}>
                {btn.icon ? IC[btn.icon] : <span className="adm2-toolbar-lbl">{btn.html}</span>}
              </button>
            ))}
          </div>
        )
      })}
    </div>
  )
}

// ── Icon Sheet ─────────────────────────────────────────
function IconSheet({ onInsert, onClose }) {
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [open, setOpen] = useState({})

  useEffect(() => {
    apiIconsGrouped().then(data => {
      setGroups(data)
      if (data[0]) setOpen({ [data[0].id]: true })
    }).finally(() => setLoading(false))
  }, [])

  const q = filter.trim().toLowerCase()
  const filtered = q
    ? groups.map(g => ({ ...g, icons: g.icons.filter(i => i.key.toLowerCase().includes(q)) })).filter(g => g.icons.length)
    : groups

  return (
    <div className="adm2-sheet-overlay" onClick={onClose}>
      <div className="adm2-sheet" onClick={e => e.stopPropagation()}>
        <div className="adm2-sheet-header">
          <span>Вставить иконку</span>
          <button className="adm2-sheet-close" onClick={onClose}>{IC.close}</button>
        </div>
        <div className="adm2-sheet-search">
          {IC.srch}
          <input className="adm2-sheet-input" placeholder="Поиск..." value={filter}
            onChange={e => setFilter(e.target.value)} autoFocus />
          {filter && <button className="adm2-clear-btn" onClick={() => setFilter('')}>{IC.close}</button>}
        </div>
        <div className="adm2-sheet-body">
          {loading && <div className="adm2-state-loading"><div className="adm2-spinner"/></div>}
          {filtered.map(group => (
            <div key={group.id}>
              <button className="adm2-sheet-grp-hdr"
                onClick={() => setOpen(p => ({ ...p, [group.id]: !p[group.id] }))}>
                <span>{group.label}</span>
                <span className="adm2-sheet-grp-count">{group.icons.length}</span>
                <span>{(q || open[group.id]) ? '▾' : '▸'}</span>
              </button>
              {(q || open[group.id]) && (
                <div className="adm2-sheet-grid">
                  {group.icons.map(icon => (
                    <button key={icon.key} className="adm2-sheet-item"
                      title={`{{${icon.key}}}`}
                      onClick={() => { onInsert(icon.key); haptic.light() }}>
                      <img src={icon.url} alt={icon.key} width={28} height={28}
                        loading="lazy" onError={e => { e.target.style.opacity='0.2' }}/>
                      <span className="adm2-sheet-key">{icon.key}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
          {!loading && !filtered.length && <div className="adm2-state-empty">Ничего не найдено</div>}
        </div>
      </div>
    </div>
  )
}

// ── Rich Editor ────────────────────────────────────────
function normalizeIcons(text) {
  return text.replace(/:(\w+):/g, (_, k) => `{{${k}}}`)
}

function renderMd(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/~~(.*?)~~/g, '<s>$1</s>')
    .replace(/\|\|(.*?)\|\|/g, '<span class="adm2-prev-spoil">$1</span>')
    .replace(/<u>(.*?)<\/u>/g, '<u>$1</u>')
    .replace(/`(.*?)`/g, '<code class="adm2-prev-code">$1</code>')
    .replace(/^### (.+)$/gm, '<h3 class="adm2-prev-h3">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="adm2-prev-h2">$1</h2>')
    .replace(/^> (.+)$/gm, '<blockquote class="adm2-prev-quote">$1</blockquote>')
    .replace(/^- (.+)$/gm, '<li class="adm2-prev-li">$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li class="adm2-prev-li adm2-prev-ol">$1</li>')
    .replace(/\[(.+?)\]\((.*?)\)/g, '<a href="$2" class="adm2-prev-link">$1</a>')
    .replace(/\[\[([^\]|]+)(?:\|([^\]]*))?\]\]/g, (_, key, label) =>
      `<span class="adm2-prev-cyber">${label || key}</span>`)
    .replace(/{{(\w+)}}/g, '<span class="adm2-prev-icon">🖼</span>')
    .replace(/\n/g, '<br>')
}

function RichEditor({ value, onChange, rows = 16, placeholder }) {
  const [showSheet, setShowSheet] = useState(false)
  const [preview, setPreview] = useState(false)
  const taRef = useRef(null)
  const words = value.trim().split(/\s+/).filter(Boolean).length

  const insertIcon = (key) => {
    const tag = `{{${key}}}`
    const el = taRef.current
    if (!el) { onChange(value + tag); setShowSheet(false); return }
    const s = el.selectionStart, e = el.selectionEnd
    const next = value.slice(0, s) + tag + value.slice(e)
    onChange(next)
    requestAnimationFrame(() => { el.focus(); el.setSelectionRange(s + tag.length, s + tag.length) })
    setShowSheet(false)
  }

  const handleChange = (e) => {
    const raw = e.target.value
    const norm = normalizeIcons(raw)
    if (norm !== raw) {
      const pos = e.target.selectionStart + (norm.length - raw.length)
      onChange(norm)
      requestAnimationFrame(() => taRef.current?.setSelectionRange(pos, pos))
    } else onChange(raw)
  }

  return (
    <div className="adm2-rich">
      <RichToolbar textareaRef={taRef} value={value} onChange={onChange} />

      <div className="adm2-rich-bar">
        <div className="adm2-mode-toggle">
          <button className={`adm2-mode-btn${!preview ? ' on' : ''}`} type="button"
            onClick={() => setPreview(false)}>Редактор</button>
          <button className={`adm2-mode-btn${preview ? ' on' : ''}`} type="button"
            onClick={() => setPreview(true)}>Превью</button>
        </div>
        <button type="button" className="adm2-icon-ins-btn" onClick={() => setShowSheet(true)}>
          🎨 Иконки
        </button>
        <span className="adm2-wc">{words} сл.</span>
      </div>

      {preview
        ? <div className="adm2-preview"
            dangerouslySetInnerHTML={{ __html: value ? renderMd(value) : '<span class="adm2-prev-ph">Предварительный просмотр...</span>' }}/>
        : <textarea ref={taRef} className="adm2-textarea" rows={rows} value={value}
            onChange={handleChange} placeholder={placeholder} spellCheck={false}/>
      }

      <div className="adm2-rich-footer">
        <code>**жирный**</code>
        <code>*курсив*</code>
        <code>~~зачёрк.~~</code>
        <code>||спойлер||</code>
        <code>`код`</code>
        <code>&gt; цитата</code>
        <code>- список</code>
        <code>[текст](url)</code>
        <code>&lt;u&gt;подчёркнутый&lt;/u&gt;</code>
        <code>[[key]] или [[key|Текст]] — киберссылка</code>
      </div>

      {showSheet && <IconSheet onInsert={insertIcon} onClose={() => setShowSheet(false)} />}
    </div>
  )
}

// ── Icon Picker ────────────────────────────────────────
function IconPicker({ value, onChange }) {
  const [icons, setIcons] = useState([])
  const [open, setOpen] = useState(false)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    if (!open || icons.length) return
    adminFetch('/api/admin/icons').then(setIcons).catch(() => {})
  }, [open])

  const filtered = filter ? icons.filter(i => i.key.toLowerCase().includes(filter.toLowerCase())) : icons

  return (
    <div className="adm2-icp">
      <div className="adm2-icp-row">
        <input className="adm2-input" value={value} onChange={e => onChange(e.target.value)} placeholder="URL иконки"/>
        <button type="button" className="adm2-icp-btn" onClick={() => setOpen(v => !v)}>
          {open ? IC.close : '🎨'}
        </button>
        {value && <IconPreview url={value}/>}
      </div>
      {open && (
        <div className="adm2-icp-panel">
          <input className="adm2-icp-filter" placeholder="Поиск..." value={filter}
            onChange={e => setFilter(e.target.value)} autoFocus/>
          <div className="adm2-icp-grid">
            {filtered.map(ic => (
              <button key={ic.key} type="button" title={ic.key} className="adm2-icp-item"
                onClick={() => { onChange(ic.url); setOpen(false); setFilter('') }}>
                <img src={ic.url} alt={ic.key} width={26} height={26}/>
              </button>
            ))}
            {!filtered.length && <span className="adm2-state-empty" style={{fontSize:'13px',padding:'8px'}}>Не найдено</span>}
          </div>
        </div>
      )}
    </div>
  )
}

function Field({ label, hint, children }) {
  return (
    <div className="adm2-field">
      <div className="adm2-field-lbl">{label}{hint && <span className="adm2-field-hint">{hint}</span>}</div>
      {children}
    </div>
  )
}

// ── Guide Editor ───────────────────────────────────────
function GuideEditor({ guide, categories, onSave, onCancel }) {
  const isNew = !guide?.key
  const [form, setForm] = useState({
    key:          guide?.key          ?? '',
    category_key: guide?.category_key ?? (categories[0]?.key ?? ''),
    title:        guide?.title        ?? '',
    icon_url:     guide?.icon_url     ?? '',
    text:         guide?.text         ?? '',
    photo:        (guide?.photo       ?? []).join('\n'),
    video:        (guide?.video       ?? []).join('\n'),
    document:     (guide?.document    ?? []).join('\n'),
    sort_order:   guide?.sort_order   ?? 0,
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState(null)
  const [tab, setTab] = useState('main')

  const set = f => e => setForm(p => ({ ...p, [f]: e.target.value }))

  const handleSave = async () => {
    if (!form.key.trim() || !form.title.trim()) { setErr('Key и Title обязательны'); return }
    setSaving(true); setErr(null)
    try {
      await adminPut(`/api/admin/guide/${form.key}`, {
        category_key: form.category_key,
        title:        form.title,
        icon_url:     form.icon_url || null,
        text:         form.text,
        photo:        form.photo.split('\n').map(s => s.trim()).filter(Boolean),
        video:        form.video.split('\n').map(s => s.trim()).filter(Boolean),
        document:     form.document.split('\n').map(s => s.trim()).filter(Boolean),
        sort_order:   Number(form.sort_order),
      })
      haptic.success(); onSave()
    } catch(e) { setErr(e.message) }
    finally { setSaving(false) }
  }

  return (
    <div className="adm2-editor">
      <div className="adm2-editor-top">
        <button className="adm2-back-btn" onClick={onCancel}>{IC.back}</button>
        <div className="adm2-editor-title">
          <div className="adm2-editor-lbl">{isNew ? 'Новый гайд' : 'Редактирование'}</div>
          <div className="adm2-editor-name">{form.title || 'Без названия'}</div>
        </div>
        <button className="adm2-save-btn" onClick={handleSave} disabled={saving}>
          {saving ? <div className="adm2-spinner adm2-spinner-sm"/> : IC.save}
          <span>{saving ? 'Сохранение...' : 'Сохранить'}</span>
        </button>
      </div>

      {err && <div className="adm2-error">{err}</div>}

      <div className="adm2-inner-tabs">
        {['main','text','media'].map(t => (
          <button key={t} className={`adm2-inner-tab${tab===t?' on':''}`} onClick={() => setTab(t)}>
            {t==='main'?'Основное':t==='text'?'Текст':'Медиа'}
          </button>
        ))}
      </div>

      <div className="adm2-editor-body">
        {tab === 'main' && (
          <div className="adm2-fields">
            <Field label="Key" hint="уникальный, без пробелов">
              <input className="adm2-input" value={form.key} onChange={set('key')} disabled={!isNew} placeholder="promo_ether"/>
            </Field>
            <Field label="Категория">
              <select className="adm2-select" value={form.category_key} onChange={set('category_key')}>
                {categories.map(c => <option key={c.key} value={c.key}>{c.title}</option>)}
              </select>
            </Field>
            <Field label="Название">
              <input className="adm2-input" value={form.title} onChange={set('title')} placeholder="Эфир | Ether"/>
            </Field>
            <Field label="Иконка">
              <IconPicker value={form.icon_url} onChange={val => setForm(p => ({ ...p, icon_url: val }))}/>
            </Field>
            <Field label="Порядок сортировки">
              <input className="adm2-input" style={{maxWidth:'100px'}} type="number" value={form.sort_order} onChange={set('sort_order')}/>
            </Field>
          </div>
        )}
        {tab === 'text' && (
          <RichEditor value={form.text} onChange={val => setForm(p => ({ ...p, text: val }))} rows={18} placeholder="Текст гайда..."/>
        )}
        {tab === 'media' && (
          <div className="adm2-fields">
            <Field label="Фото" hint="по одному URL на строку">
              <textarea className="adm2-textarea" rows={4} value={form.photo} onChange={set('photo')} placeholder="https://..."/>
            </Field>
            <Field label="Видео" hint="по одному URL на строку">
              <textarea className="adm2-textarea" rows={3} value={form.video} onChange={set('video')} placeholder="https://..."/>
            </Field>
            <Field label="Документы" hint="по одному URL на строку">
              <textarea className="adm2-textarea" rows={3} value={form.document} onChange={set('document')} placeholder="https://..."/>
            </Field>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Guides Tab ─────────────────────────────────────────
function GuidesTab({ categories }) {
  const [guides, setGuides] = useState([])
  const [catFilter, setCatFilter] = useState('')
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState(null)
  const [loading, setLoading] = useState(false)
  const [deleting, setDeleting] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const path = catFilter ? `/api/admin/guides?category_key=${catFilter}` : '/api/admin/guides'
      setGuides(await adminFetch(path))
    } finally { setLoading(false) }
  }, [catFilter])

  useEffect(() => { load() }, [load])

  const handleDelete = async (g) => {
    if (!window.confirm(`Удалить гайд "${g.title}"?`)) return
    setDeleting(g.key)
    try { await adminDelete(`/api/admin/guide/${g.key}`); haptic.success(); load() }
    catch(e) { alert(e.message) }
    finally { setDeleting(null) }
  }

  const handleEdit = async (g) => {
    const full = await adminFetch(`/api/admin/guide/${g.key}`)
    setEditing(full)
  }

  if (editing !== null) return (
    <GuideEditor guide={editing === 'new' ? null : editing} categories={categories}
      onSave={() => { setEditing(null); load() }} onCancel={() => setEditing(null)}/>
  )

  const visible = guides.filter(g =>
    !search || g.title.toLowerCase().includes(search.toLowerCase()) || g.key.includes(search)
  )

  return (
    <div className="adm2-tab-content">
      <div className="adm2-list-toolbar">
        <div className="adm2-srch-wrap">
          {IC.srch}
          <input className="adm2-srch-input" placeholder="Поиск гайдов..."
            value={search} onChange={e => setSearch(e.target.value)}/>
        </div>
        <select className="adm2-filter-sel" value={catFilter} onChange={e => setCatFilter(e.target.value)}>
          <option value="">Все</option>
          {categories.map(c => <option key={c.key} value={c.key}>{c.title}</option>)}
        </select>
        <button className="adm2-add-btn" onClick={() => setEditing('new')}>{IC.plus}</button>
      </div>

      {loading && <div className="adm2-state-loading"><div className="adm2-spinner"/></div>}

      <ReorderList
        items={visible}
        onReorder={async (newOrder) => {
          const order = newOrder.map((g, i) => ({ key: g.key, sort_order: i * 10 }))
          await apiReorderGuides(order).catch(() => {})
        }}
        renderItem={(g) => (
          <div className="adm2-item" style={{background:'var(--surface)',border:'1px solid var(--separator)',borderRadius:'var(--radius)',padding:'11px 12px',display:'flex',alignItems:'center',gap:'12px'}}>
            <IconPreview url={g.icon_url}/>
            <div className="adm2-item-info">
              <div className="adm2-item-title">{g.title}</div>
              <div className="adm2-item-sub">
                <span className="adm2-item-key">{g.key}</span>
                <span className="adm2-item-sep">·</span>
                <span>{categories.find(c => c.key === g.category_key)?.title ?? g.category_key}</span>
              </div>
            </div>
            <div className="adm2-item-acts">
              <button className="adm2-item-btn" onClick={() => handleEdit(g)}>{IC.edit}</button>
              <button className="adm2-item-btn adm2-item-btn-del" onClick={() => handleDelete(g)} disabled={deleting === g.key}>
                {deleting === g.key ? <div className="adm2-spinner adm2-spinner-sm"/> : IC.trash}
              </button>
            </div>
          </div>
        )}
      />
      {!loading && !visible.length && (
          <div className="adm2-state-empty">{search ? 'Ничего не найдено' : 'Нет гайдов. Создайте первый!'}</div>
        )}
      </div>

      {guides.length > 0 && (
        <div className="adm2-list-footer">{visible.length} из {guides.length} гайдов</div>
      )}
    </div>
  )
}

// ── Categories Tab ─────────────────────────────────────
function CategoriesTab({ categories, onReload }) {
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ key:'', title:'', icon_url:'', sort_order:0 })
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(null)
  const [err, setErr] = useState(null)

  const set = f => e => setForm(p => ({ ...p, [f]: e.target.value }))

  const handleSave = async () => {
    if (!form.key.trim() || !form.title.trim()) { setErr('Key и Title обязательны'); return }
    setSaving(true); setErr(null)
    try {
      await adminPut(`/api/admin/category/${form.key}`, {
        title: form.title, icon_url: form.icon_url||null, sort_order: Number(form.sort_order)
      })
      haptic.success(); setEditing(null); onReload()
    } catch(e) { setErr(e.message) }
    finally { setSaving(false) }
  }

  const handleDelete = async (cat) => {
    if (!window.confirm(`Удалить категорию "${cat.title}" и все её гайды?`)) return
    setDeleting(cat.key)
    try { await adminDelete(`/api/admin/category/${cat.key}`); haptic.success(); onReload() }
    catch(e) { alert(e.message) }
    finally { setDeleting(null) }
  }

  if (editing !== null) return (
    <div className="adm2-editor">
      <div className="adm2-editor-top">
        <button className="adm2-back-btn" onClick={() => setEditing(null)}>{IC.back}</button>
        <div className="adm2-editor-title">
          <div className="adm2-editor-lbl">{editing === 'new' ? 'Новая категория' : 'Категория'}</div>
          <div className="adm2-editor-name">{form.title || 'Без названия'}</div>
        </div>
        <button className="adm2-save-btn" onClick={handleSave} disabled={saving}>
          {saving ? <div className="adm2-spinner adm2-spinner-sm"/> : IC.save}
          <span>{saving ? 'Сохранение...' : 'Сохранить'}</span>
        </button>
      </div>
      {err && <div className="adm2-error">{err}</div>}
      <div className="adm2-editor-body">
        <div className="adm2-fields">
          <Field label="Key">
            <input className="adm2-input" value={form.key} onChange={set('key')} disabled={editing !== 'new'} placeholder="cat_promoutes"/>
          </Field>
          <Field label="Название">
            <input className="adm2-input" value={form.title} onChange={set('title')} placeholder="Промоуты"/>
          </Field>
          <Field label="Иконка">
            <IconPicker value={form.icon_url} onChange={val => setForm(p => ({ ...p, icon_url: val }))}/>
          </Field>
          <Field label="Порядок">
            <input className="adm2-input" style={{maxWidth:'100px'}} type="number" value={form.sort_order} onChange={set('sort_order')}/>
          </Field>
        </div>
      </div>
    </div>
  )

  return (
    <div className="adm2-tab-content">
      <div className="adm2-list-toolbar" style={{justifyContent:'flex-end'}}>
        <span className="adm2-count-lbl">{categories.length} категорий</span>
        <button className="adm2-add-btn" onClick={() => { setForm({key:'',title:'',icon_url:'',sort_order:categories.length}); setEditing('new') }}>{IC.plus}</button>
      </div>
      <div className="adm2-list">
        {categories.map(cat => (
          <div key={cat.key} className="adm2-item">
            <IconPreview url={cat.icon_url}/>
            <div className="adm2-item-info">
              <div className="adm2-item-title">{cat.title}</div>
              <div className="adm2-item-sub">
                <span className="adm2-item-key">{cat.key}</span>
                <span className="adm2-item-sep">·</span>
                <span>порядок: {cat.sort_order}</span>
              </div>
            </div>
            <div className="adm2-item-acts">
              <button className="adm2-item-btn"
                onClick={() => { setForm({key:cat.key,title:cat.title,icon_url:cat.icon_url||'',sort_order:cat.sort_order}); setEditing(cat.key) }}>
                {IC.edit}
              </button>
              <button className="adm2-item-btn adm2-item-btn-del" onClick={() => handleDelete(cat)} disabled={deleting === cat.key}>
                {deleting === cat.key ? <div className="adm2-spinner adm2-spinner-sm"/> : IC.trash}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Main ───────────────────────────────────────────────
export function AdminView({ onClose }) {
  const [tab, setTab] = useState('guides')
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    try {
      setCategories(await adminFetch('/api/admin/categories'))
    } catch(e) {
      setError(e.message === 'ACCESS_DENIED' ? 'Нет прав администратора' : e.message)
    } finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) return (
    <div className="adm2-wrap">
      <div className="adm2-state-loading" style={{height:'100%'}}><div className="adm2-spinner"/></div>
    </div>
  )

  if (error) return (
    <div className="adm2-wrap">
      <div className="adm2-top-bar">
        <span className="adm2-top-title">Администрирование</span>
        <button className="adm2-close-btn" onClick={onClose}>{IC.close}</button>
      </div>
      <div style={{padding:'24px'}}>
        <div className="adm2-error">{error}</div>
        <p style={{color:'var(--text-secondary)',fontSize:'14px',marginTop:'12px',lineHeight:1.5}}>
          Используйте <strong>/admin</strong> в боте и открывайте через inline-кнопку.
        </p>
      </div>
    </div>
  )

  return (
    <div className="adm2-wrap">
      <div className="adm2-top-bar">
        <span className="adm2-top-title">Администрирование</span>
        <button className="adm2-close-btn" onClick={onClose}>{IC.close}</button>
      </div>
      <div className="adm2-tabs">
        {[['guides','Гайды'],['categories','Категории'],['icons','🎨 Иконки'],['export','Экспорт']].map(([id, lbl]) => (
          <button key={id} className={`adm2-tab${tab===id?' active':''}`} onClick={() => setTab(id)}>{lbl}</button>
        ))}
      </div>
      <div className="adm2-content">
        {tab === 'guides'     && <GuidesTab categories={categories}/>}
        {tab === 'categories' && <CategoriesTab categories={categories} onReload={load}/>}
        {tab === 'icons'      && <IconLibrary/>}
        {tab === 'export'     && <ExportImport/>}
      </div>
    </div>
  )
}
