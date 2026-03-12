import { useState, useEffect, useCallback } from 'react'
import { apiFetch, apiPost, apiPut, apiDelete } from '../api'
import { haptic } from '../haptic'

// ── API helpers ───────────────────────────────────────
const adminFetch  = (path)         => apiFetch(path)
const adminPut    = (path, body)   => apiPut(path, body)
const adminDelete = (path)         => apiDelete(path)

// ── Sub-views ─────────────────────────────────────────
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
        <h3>{isNew ? 'Новый гайд' : 'Редактировать гайд'}</h3>
      </div>
      {err && <div className="admin-error">{err}</div>}
      <div className="admin-form">
        <label>Key (уникальный, без пробелов)</label>
        <input value={form.key} onChange={set('key')} disabled={!isNew} placeholder="promo_ether" />

        <label>Категория</label>
        <select value={form.category_key} onChange={set('category_key')}>
          {categories.map(c => <option key={c.key} value={c.key}>{c.title}</option>)}
        </select>

        <label>Название</label>
        <input value={form.title} onChange={set('title')} placeholder="Эфир | Ether" />

        <label>Icon URL (или ключ иконки)</label>
        <input value={form.icon_url} onChange={set('icon_url')} placeholder="https://..." />

        <label>Текст (используй {'{{icon_name}}'} и **жирный**)</label>
        <textarea rows={12} value={form.text} onChange={set('text')} placeholder="Текст гайда..." />

        <label>Фото (по одному URL на строку)</label>
        <textarea rows={3} value={form.photo} onChange={set('photo')} placeholder="https://..." />

        <label>Видео (по одному URL на строку)</label>
        <textarea rows={2} value={form.video} onChange={set('video')} placeholder="https://..." />

        <label>Документы (по одному URL на строку)</label>
        <textarea rows={2} value={form.document} onChange={set('document')} placeholder="https://..." />

        <label>Порядок сортировки</label>
        <input type="number" value={form.sort_order} onChange={set('sort_order')} />
      </div>
      <div className="admin-actions">
        <button className="btn-secondary" onClick={onCancel}>Отмена</button>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? 'Сохранение...' : 'Сохранить'}
        </button>
      </div>
    </div>
  )
}


function GuidesTab({ categories }) {
  const [guides, setGuides]     = useState([])
  const [catFilter, setCatFilter] = useState('')
  const [editing, setEditing]   = useState(null) // null | 'new' | guide object
  const [loading, setLoading]   = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const path = catFilter ? `/api/admin/guides?category_key=${catFilter}` : '/api/admin/guides'
      setGuides(await adminFetch(path))
    } finally { setLoading(false) }
  }, [catFilter])

  useEffect(() => { load() }, [load])

  const handleDelete = async (g) => {
    if (!confirm(`Удалить гайд "${g.title}"?`)) return
    await adminDelete(`/api/admin/guide/${g.key}`)
    haptic.success()
    load()
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
        <button className="btn-primary" onClick={() => setEditing('new')}>+ Новый гайд</button>
      </div>
      {loading && <div className="admin-loading">Загрузка...</div>}
      <div className="admin-list">
        {guides.map(g => (
          <div key={g.key} className="admin-item">
            {g.icon_url && <img src={g.icon_url} alt="" width={32} height={32} className="admin-item-icon"/>}
            <div className="admin-item-info">
              <div className="admin-item-title">{g.title}</div>
              <div className="admin-item-sub">{g.key} · {categories.find(c=>c.key===g.category_key)?.title}</div>
            </div>
            <div className="admin-item-btns">
              <button onClick={() => handleEdit(g)}>✏️</button>
              <button onClick={() => handleDelete(g)}>🗑️</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}


function CategoriesTab({ categories, onReload }) {
  const [editing, setEditing] = useState(null)
  const [form, setForm]       = useState({key:'',title:'',icon_url:'',sort_order:0})
  const [saving, setSaving]   = useState(false)
  const [err, setErr]         = useState(null)

  const openEdit = (cat) => {
    setForm({key: cat.key, title: cat.title, icon_url: cat.icon_url||'', sort_order: cat.sort_order})
    setEditing(cat.key)
  }

  const openNew = () => {
    setForm({key:'',title:'',icon_url:'',sort_order: categories.length})
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
    if (!confirm(`Удалить категорию "${cat.title}" и все её гайды?`)) return
    await adminDelete(`/api/admin/category/${cat.key}`)
    haptic.success(); onReload()
  }

  const set = (f) => (e) => setForm(v => ({...v, [f]: e.target.value}))

  if (editing !== null) return (
    <div className="admin-editor">
      <div className="admin-editor-header">
        <h3>{editing === 'new' ? 'Новая категория' : 'Редактировать категорию'}</h3>
      </div>
      {err && <div className="admin-error">{err}</div>}
      <div className="admin-form">
        <label>Key</label>
        <input value={form.key} onChange={set('key')} disabled={editing !== 'new'} placeholder="cat_promoutes"/>
        <label>Название</label>
        <input value={form.title} onChange={set('title')} placeholder="Промоуты"/>
        <label>Icon URL</label>
        <input value={form.icon_url} onChange={set('icon_url')} placeholder="https://..."/>
        <label>Порядок</label>
        <input type="number" value={form.sort_order} onChange={set('sort_order')}/>
      </div>
      <div className="admin-actions">
        <button className="btn-secondary" onClick={() => setEditing(null)}>Отмена</button>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>{saving?'...':'Сохранить'}</button>
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
            {cat.icon_url && <img src={cat.icon_url} alt="" width={32} height={32} className="admin-item-icon"/>}
            <div className="admin-item-info">
              <div className="admin-item-title">{cat.title}</div>
              <div className="admin-item-sub">{cat.key}</div>
            </div>
            <div className="admin-item-btns">
              <button onClick={() => openEdit(cat)}>✏️</button>
              <button onClick={() => handleDelete(cat)}>🗑️</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}


// ── Main AdminView ────────────────────────────────────
export function AdminView({ onClose }) {
  const [tab, setTab]             = useState('guides')
  const [categories, setCategories] = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)

  const loadCategories = useCallback(async () => {
    try {
      const data = await adminFetch('/api/admin/categories')
      setCategories(data)
    } catch(e) {
      setError(e.message === 'ACCESS_DENIED' ? 'Нет прав администратора' : e.message)
    } finally { setLoading(false) }
  }, [])

  useEffect(() => { loadCategories() }, [loadCategories])

  if (loading) return <div className="admin-wrap"><div className="admin-loading">Загрузка...</div></div>
  if (error)   return <div className="admin-wrap"><div className="admin-error">{error}</div></div>

  return (
    <div className="admin-wrap">
      <div className="admin-header">
        <h2>Администрирование</h2>
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
