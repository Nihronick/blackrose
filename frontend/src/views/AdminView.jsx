import { useState, useEffect, useCallback } from 'react'
import { apiFetch, apiPut, apiDelete } from '../api'
import { haptic } from '../haptic'

// ── API helpers ───────────────────────────────────────
const adminFetch  = (path)       => apiFetch(path)
const adminPut    = (path, body) => apiPut(path, body)
const adminDelete = (path)       => apiDelete(path)

// ── Icon preview ──────────────────────────────────────
function IconPreview({ url }) {
  if (!url) return <div className="icon-preview-empty">?</div>
  return <img src={url} alt="" width={32} height={32} className="icon-preview-img"
    onError={e => { e.target.style.display='none' }} />
}

// ── Icon picker ───────────────────────────────────────
function IconPicker({ value, onChange }) {
  const [icons, setIcons]   = useState([])
  const [open, setOpen]     = useState(false)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    if (!open || icons.length) return
    adminFetch('/api/admin/icons').then(setIcons).catch(() => {})
  }, [open])

  const filtered = filter
    ? icons.filter(i => i.key.toLowerCase().includes(filter.toLowerCase()))
    : icons

  return (
    <div className="icon-picker">
      <div className="icon-picker-row">
        <input value={value} onChange={e => onChange(e.target.value)} placeholder="URL или ключ иконки" />
        <button type="button" className="btn-icon-pick" onClick={() => setOpen(v => !v)}>
          {open ? '✕' : '🎨'}
        </button>
        {value && <IconPreview url={value} />}
      </div>
      {open && (
        <div className="icon-picker-panel">
          <input
            className="icon-picker-filter"
            placeholder="Поиск иконки..."
            value={filter}
            onChange={e => setFilter(e.target.value)}
            autoFocus
          />
          <div className="icon-picker-grid">
            {filtered.map(ic => (
              <button key={ic.key} type="button" title={ic.key}
                className="icon-picker-item"
                onClick={() => { onChange(ic.url); setOpen(false); setFilter('') }}>
                <img src={ic.url} alt={ic.key} width={28} height={28} />
              </button>
            ))}
            {filtered.length === 0 && <span className="icon-picker-empty">Не найдено</span>}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Guide Editor ──────────────────────────────────────
function GuideEditor({ guide, categories, onSave, onCancel }) {
  const isNew = !guide?.key
  const [form, setForm] = useState({
    key:          guide?.key          ?? '',
    category_key: guide?.category_key ?? (categories[0]?.key ?? ''),
    title:        guide?.title        ?? '',
    icon_url:     guide?.icon_url     ?? '',
    text:         guide?.text         ?? '',
    photo:        (guide?.photo  ?? []).join('\n'),
    video:        (guide?.video  ?? []).join('\n'),
    document:     (guide?.document ?? []).join('\n'),
    sort_order:   guide?.sort_order   ?? 0,
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr]       = useState(null)

  const set = (field) => (e) => setForm(f => ({...f, [field]: e.target.value}))

  const handleSave = async () => {
    if (!form.key.trim() || !form.title.trim()) { setErr('Key и Title обязательны'); return }
    setSaving(true); setErr(null)
    try {
      await adminPut(`/api/admin/guide/${form.key}`, {
        category_key: form.category_key,
        title:        form.title,
        icon_url:     form.icon_url || null,
        text:         form.text,
        photo:        form.photo.split('\n').map(s=>s.trim()).filter(Boolean),
        video:        form.video.split('\n').map(s=>s.trim()).filter(Boolean),
        document:     form.document.split('\n').map(s=>s.trim()).filter(Boolean),
        sort_order:   Number(form.sort_order),
      })
      haptic.success()
      onSave()
    } catch(e) { setErr(e.message) }
    finally { setSaving(false) }
  }

  return (
    <div className="admin-editor">
      <div className="admin-editor-header">
        <h3>{isNew ? '✨ Новый гайд' : '✏️ Редактировать гайд'}</h3>
      </div>
      {err && <div className="admin-error">⚠️ {err}</div>}
      <div className="admin-form">
        <label>Key <span className="label-hint">(уникальный, без пробелов)</span></label>
        <input value={form.key} onChange={set('key')} disabled={!isNew} placeholder="promo_ether" />

        <label>Категория</label>
        <select value={form.category_key} onChange={set('category_key')}>
          {categories.map(c => <option key={c.key} value={c.key}>{c.title}</option>)}
        </select>

        <label>Название</label>
        <input value={form.title} onChange={set('title')} placeholder="Эфир | Ether" />

        <label>Иконка</label>
        <IconPicker value={form.icon_url} onChange={val => setForm(f=>({...f, icon_url: val}))} />

        <label>Текст <span className="label-hint">— {`{{icon_name}}`} для иконок, **жирный**, *курсив*</span></label>
        <textarea rows={12} value={form.text} onChange={set('text')} placeholder="Текст гайда..." />

        <label>Фото <span className="label-hint">(по одному URL на строку)</span></label>
        <textarea rows={3} value={form.photo} onChange={set('photo')} placeholder="https://..." />

        <label>Видео <span className="label-hint">(по одному URL на строку)</span></label>
        <textarea rows={2} value={form.video} onChange={set('video')} placeholder="https://..." />

        <label>Документы <span className="label-hint">(по одному URL на строку)</span></label>
        <textarea rows={2} value={form.document} onChange={set('document')} placeholder="https://..." />

        <label>Порядок сортировки</label>
        <input type="number" value={form.sort_order} onChange={set('sort_order')} />
      </div>
      <div className="admin-actions">
        <button className="btn-secondary" onClick={onCancel} disabled={saving}>Отмена</button>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? '⏳ Сохранение...' : '✅ Сохранить'}
        </button>
      </div>
    </div>
  )
}


// ── Guides Tab ────────────────────────────────────────
function GuidesTab({ categories }) {
  const [guides, setGuides]       = useState([])
  const [catFilter, setCatFilter] = useState('')
  const [editing, setEditing]     = useState(null)
  const [loading, setLoading]     = useState(false)
  const [deleting, setDeleting]   = useState(null)

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
    try {
      await adminDelete(`/api/admin/guide/${g.key}`)
      haptic.success()
      load()
    } catch(e) { alert(e.message) }
    finally { setDeleting(null) }
  }

  const handleEdit = async (g) => {
    const full = await adminFetch(`/api/admin/guide/${g.key}`)
    setEditing(full)
  }

  if (editing !== null) {
    return (
      <GuideEditor
        guide={editing === 'new' ? null : editing}
        categories={categories}
        onSave={() => { setEditing(null); load() }}
        onCancel={() => setEditing(null)}
      />
    )
  }

  return (
    <div>
      <div className="admin-toolbar">
        <select value={catFilter} onChange={e => setCatFilter(e.target.value)}>
          <option value="">Все категории</option>
          {categories.map(c => <option key={c.key} value={c.key}>{c.title}</option>)}
        </select>
        <button className="btn-primary" onClick={() => setEditing('new')}>+ Новый</button>
      </div>
      {loading && <div className="admin-loading">⏳ Загрузка...</div>}
      <div className="admin-list">
        {guides.map(g => (
          <div key={g.key} className="admin-item">
            <IconPreview url={g.icon_url} />
            <div className="admin-item-info">
              <div className="admin-item-title">{g.title}</div>
              <div className="admin-item-sub">
                {g.key} · {categories.find(c=>c.key===g.category_key)?.title ?? g.category_key}
              </div>
            </div>
            <div className="admin-item-btns">
              <button onClick={() => handleEdit(g)} title="Редактировать">✏️</button>
              <button
                onClick={() => handleDelete(g)}
                disabled={deleting === g.key}
                className="btn-danger"
                title="Удалить"
              >
                {deleting === g.key ? '⏳' : '🗑️'}
              </button>
            </div>
          </div>
        ))}
        {!loading && guides.length === 0 && (
          <div className="state-empty">Гайдов нет. Создайте первый!</div>
        )}
      </div>
    </div>
  )
}


// ── Categories Tab ────────────────────────────────────
function CategoriesTab({ categories, onReload }) {
  const [editing, setEditing]   = useState(null)
  const [form, setForm]         = useState({key:'',title:'',icon_url:'',sort_order:0})
  const [saving, setSaving]     = useState(false)
  const [deleting, setDeleting] = useState(null)
  const [err, setErr]           = useState(null)

  const openEdit = (cat) => {
    setForm({key: cat.key, title: cat.title, icon_url: cat.icon_url||'', sort_order: cat.sort_order})
    setEditing(cat.key)
  }

  const openNew = () => {
    setForm({key:'', title:'', icon_url:'', sort_order: categories.length})
    setEditing('new')
  }

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
    try {
      await adminDelete(`/api/admin/category/${cat.key}`)
      haptic.success(); onReload()
    } catch(e) { alert(e.message) }
    finally { setDeleting(null) }
  }

  const set = (f) => (e) => setForm(v => ({...v, [f]: e.target.value}))

  if (editing !== null) return (
    <div className="admin-editor">
      <div className="admin-editor-header">
        <h3>{editing === 'new' ? '✨ Новая категория' : '✏️ Редактировать категорию'}</h3>
      </div>
      {err && <div className="admin-error">⚠️ {err}</div>}
      <div className="admin-form">
        <label>Key</label>
        <input value={form.key} onChange={set('key')} disabled={editing !== 'new'} placeholder="cat_promoutes"/>
        <label>Название</label>
        <input value={form.title} onChange={set('title')} placeholder="Промоуты"/>
        <label>Иконка</label>
        <IconPicker value={form.icon_url} onChange={val => setForm(v=>({...v, icon_url: val}))} />
        <label>Порядок</label>
        <input type="number" value={form.sort_order} onChange={set('sort_order')}/>
      </div>
      <div className="admin-actions">
        <button className="btn-secondary" onClick={() => setEditing(null)} disabled={saving}>Отмена</button>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? '⏳ Сохранение...' : '✅ Сохранить'}
        </button>
      </div>
    </div>
  )

  return (
    <div>
      <div className="admin-toolbar">
        <span>{categories.length} категорий</span>
        <button className="btn-primary" onClick={openNew}>+ Новая</button>
      </div>
      <div className="admin-list">
        {categories.map(cat => (
          <div key={cat.key} className="admin-item">
            <IconPreview url={cat.icon_url} />
            <div className="admin-item-info">
              <div className="admin-item-title">{cat.title}</div>
              <div className="admin-item-sub">{cat.key} · порядок: {cat.sort_order}</div>
            </div>
            <div className="admin-item-btns">
              <button onClick={() => openEdit(cat)} title="Редактировать">✏️</button>
              <button
                onClick={() => handleDelete(cat)}
                disabled={deleting === cat.key}
                className="btn-danger"
                title="Удалить категорию и все её гайды"
              >
                {deleting === cat.key ? '⏳' : '🗑️'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}


// ── Main AdminView ────────────────────────────────────
export function AdminView({ onClose }) {
  const [tab, setTab]               = useState('guides')
  const [categories, setCategories] = useState([])
  const [loading, setLoading]       = useState(true)
  const [error, setError]           = useState(null)

  const loadCategories = useCallback(async () => {
    try {
      const data = await adminFetch('/api/admin/categories')
      setCategories(data)
    } catch(e) {
      setError(e.message === 'ACCESS_DENIED' ? 'Нет прав администратора' : e.message)
    } finally { setLoading(false) }
  }, [])

  useEffect(() => { loadCategories() }, [loadCategories])

  if (loading) return <div className="admin-wrap"><div className="admin-loading">⏳ Загрузка...</div></div>
  if (error) return (
    <div className="admin-wrap">
      <div className="admin-header">
        <h2>⚙️ Администрирование</h2>
        <button className="admin-close" onClick={onClose}>✕</button>
      </div>
      <div style={{padding:'24px'}}>
        <div className="admin-error">⚠️ {error}</div>
        <p style={{color:'var(--text-secondary)', fontSize:'14px', marginTop:'12px'}}>
          Для доступа к панели администратора используйте команду <b>/admin</b> в боте
          и открывайте приложение через inline-кнопку которую пришлёт бот.
        </p>
      </div>
    </div>
  )

  return (
    <div className="admin-wrap">
      <div className="admin-header">
        <h2>⚙️ Администрирование</h2>
        <button className="admin-close" onClick={onClose}>✕</button>
      </div>

      <div className="admin-tabs">
        <button className={tab==='guides'     ? 'active':''} onClick={()=>setTab('guides')}>Гайды</button>
        <button className={tab==='categories' ? 'active':''} onClick={()=>setTab('categories')}>Категории</button>
      </div>

      <div className="admin-content">
        {tab === 'guides'     && <GuidesTab categories={categories} />}
        {tab === 'categories' && <CategoriesTab categories={categories} onReload={loadCategories} />}
      </div>
    </div>
  )
}
