import { useState, useRef } from 'react'
import { apiExport, apiImport } from '../api'
import { haptic } from '../haptic'

export function ExportImport() {
  const [exporting, setExporting] = useState(false)
  const [importing, setImporting] = useState(false)
  const [result, setResult]       = useState(null)
  const [error, setError]         = useState(null)
  const fileRef = useRef(null)

  const handleExport = async () => {
    setExporting(true); setError(null); setResult(null)
    try {
      const data = await apiExport()
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href = url
      a.download = `blackrose-export-${new Date().toISOString().slice(0,10)}.json`
      a.click()
      URL.revokeObjectURL(url)
      haptic.success()
      setResult(`Экспортировано: ${data.categories.length} категорий, ${data.guides.length} гайдов`)
    } catch(e) { setError(e.message) }
    finally { setExporting(false) }
  }

  const handleImport = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true); setError(null); setResult(null)
    try {
      const text = await file.text()
      const data = JSON.parse(text)
      const res  = await apiImport(data)
      haptic.success()
      setResult(`Импортировано: ${res.categories} категорий, ${res.guides} гайдов`)
    } catch(e) { setError(e.message || 'Ошибка импорта') }
    finally { setImporting(false); e.target.value = '' }
  }

  return (
    <div className="adm2-tab-content">
      <div style={{display:'flex', flexDirection:'column', gap:'16px', maxWidth:'400px'}}>

        <div className="adm2-field">
          <div className="adm2-field-lbl">Экспорт</div>
          <p style={{fontSize:'13px', color:'var(--text-secondary)', marginBottom:'8px', lineHeight:1.5}}>
            Скачать все категории и гайды в JSON-файл. Используйте для резервного копирования.
          </p>
          <button
            className="adm2-save-btn"
            style={{width:'100%', justifyContent:'center'}}
            onClick={handleExport}
            disabled={exporting}
          >
            {exporting ? <div className="adm2-spinner adm2-spinner-sm"/> : '⬇️'}
            <span>{exporting ? 'Экспорт...' : 'Скачать JSON'}</span>
          </button>
        </div>

        <div className="adm2-field">
          <div className="adm2-field-lbl">Импорт</div>
          <p style={{fontSize:'13px', color:'var(--text-secondary)', marginBottom:'8px', lineHeight:1.5}}>
            Загрузить ранее экспортированный JSON. Данные будут добавлены/обновлены (существующие не удаляются).
          </p>
          <input
            ref={fileRef}
            type="file"
            accept=".json"
            style={{display:'none'}}
            onChange={handleImport}
          />
          <button
            className="btn-secondary"
            style={{width:'100%'}}
            onClick={() => fileRef.current?.click()}
            disabled={importing}
          >
            {importing ? '⏳ Импорт...' : '⬆️ Загрузить JSON'}
          </button>
        </div>

        {result && (
          <div style={{
            background:'rgba(52,199,89,.12)', color:'#27ae60',
            padding:'12px', borderRadius:'var(--radius)', fontSize:'14px',
            borderLeft:'3px solid #27ae60'
          }}>
            ✅ {result}
          </div>
        )}
        {error && <div className="adm2-error">❌ {error}</div>}
      </div>
    </div>
  )
}
