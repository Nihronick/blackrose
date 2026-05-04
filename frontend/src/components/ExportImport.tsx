import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { AlertCircle, CheckCircle2, Database, Download, Upload } from '@/lib/icons'
import type { Category, Guide } from '@/lib/types'
import type React from 'react'
import { useRef, useState } from 'react'
import { apiExport, apiImport } from '../lib/api'
import { haptic } from '../lib/haptic'

interface ExportData {
  categories: Category[]
  guides: Guide[]
}

interface ImportResponse {
  categories: number
  guides: number
}

/**
 * ExportImport — Tool for backing up and restoring database content via JSON.
 */
export const ExportImport: React.FC = () => {
  const [exporting, setExporting] = useState(false)
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleExport = async () => {
    setExporting(true)
    setError(null)
    setResult(null)
    try {
      const data = (await apiExport()) as ExportData
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `blackrose-export-${new Date().toISOString().slice(0, 10)}.json`
      a.click()
      URL.revokeObjectURL(url)
      haptic.success()
      setResult(`Экспортировано: ${data.categories.length} категорий, ${data.guides.length} гайдов`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Неизвестная ошибка')
    } finally {
      setExporting(false)
    }
  }

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    setError(null)
    setResult(null)
    try {
      const text = await file.text()
      const data = JSON.parse(text)
      const res = (await apiImport(data)) as ImportResponse
      haptic.success()
      setResult(`Импортировано: ${res.categories} категорий, ${res.guides} гайдов`)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Ошибка импорта')
    } finally {
      setImporting(false)
      if (e.target) e.target.value = ''
    }
  }

  return (
    <div className="adm2-tab-content h-full bg-background/50">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-primary/10 rounded-xl text-primary">
            <Database className="size-5" />
          </div>
          <h2 className="text-xl font-bold tracking-tight">Управление данными</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Export Card */}
          <Card className="p-6 border-border/50 bg-card/50 backdrop-blur-sm space-y-4">
            <div className="flex items-center gap-2 font-bold text-sm">
              <Download className="size-4 text-blue-500" />
              Экспорт данных
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Скачать все категории и гайды в JSON-файл. Используйте для регулярного резервного
              копирования и переноса контента.
            </p>
            <Button
              className="w-full h-11 rounded-xl font-bold transition-all active:scale-95"
              onClick={handleExport}
              disabled={exporting}
            >
              {exporting ? (
                <div className="adm2-spinner adm2-spinner-sm" />
              ) : (
                <Download className="size-4 mr-2" />
              )}
              <span>{exporting ? 'Готовим файл...' : 'Скачать JSON'}</span>
            </Button>
          </Card>

          {/* Import Card */}
          <Card className="p-6 border-border/50 bg-card/50 backdrop-blur-sm space-y-4">
            <div className="flex items-center gap-2 font-bold text-sm">
              <Upload className="size-4 text-orange-500" />
              Импорт данных
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Загрузить ранее экспортированный JSON. Данные будут добавлены или обновлены
              (существующие записи не удаляются).
            </p>
            <input
              ref={fileRef}
              type="file"
              accept=".json"
              className="hidden"
              onChange={handleImport}
            />
            <Button
              variant="secondary"
              className="w-full h-11 rounded-xl font-bold border-border/50 hover:bg-muted transition-all active:scale-95"
              onClick={() => fileRef.current?.click()}
              disabled={importing}
            >
              {importing ? (
                <div className="adm2-spinner adm2-spinner-sm" />
              ) : (
                <Upload className="size-4 mr-2" />
              )}
              <span>{importing ? 'Загрузка...' : 'Выбрать файл'}</span>
            </Button>
          </Card>
        </div>

        {/* Status Messages */}
        {result && (
          <div className="flex items-start gap-3 p-4 bg-green-500/10 border border-green-500/20 rounded-2xl animate-in zoom-in-95 duration-200">
            <CheckCircle2 className="size-5 text-green-500 shrink-0" />
            <div className="text-sm font-semibold text-green-600">{result}</div>
          </div>
        )}

        {error && (
          <div className="flex items-start gap-3 p-4 bg-destructive/10 border border-destructive/20 rounded-2xl animate-in zoom-in-95 duration-200">
            <AlertCircle className="size-5 text-destructive shrink-0" />
            <div className="text-sm font-semibold text-destructive">Ошибка: {error}</div>
          </div>
        )}

        {/* Technical Warning */}
        <div className="p-4 bg-muted/40 rounded-2xl border border-dashed border-border/50">
          <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest text-center">
            ⚠️ будьте внимательны · импорт перезаписывает контент с совпадающими ключами
          </p>
        </div>
      </div>
    </div>
  )
}
