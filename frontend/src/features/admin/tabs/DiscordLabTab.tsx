import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Beaker, Copy, Globe, RefreshCcw, Send, Settings, Database } from '@/lib/icons'
import type React from 'react'
import { useState, useMemo, useEffect } from 'react'
import { getGameIconUrl } from '@/lib/gameIcons'
import { apiFetch, apiPost, apiPut, apiImportMedia, apiGetProxyUrl } from '@/lib/api'
import type { Guide, Category } from '@/lib/types'

export const DiscordLabTab: React.FC = () => {
  const [jsonInput, setJsonInput] = useState('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [isTranslating, setIsTranslating] = useState(false)
  const [importProgress, setImportProgress] = useState({ current: 0, total: 0, status: '' })
  const [editableTitle, setEditableTitle] = useState('')
  const [selectedGuideKey, setSelectedGuideKey] = useState<string>('new')
  const [allGuides, setAllGuides] = useState<Guide[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')

  useEffect(() => {
    apiFetch<Guide[]>('/api/admin/guides').then(setAllGuides).catch(() => {})
    apiFetch<Category[]>('/api/admin/categories').then(cats => {
      setCategories(cats)
      if (cats.length > 0) setSelectedCategory(cats[0].key)
    }).catch(() => {})
  }, [])

  const runTest = async () => {
    if (!jsonInput.trim()) return
    setLoading(true)
    try {
      await new Promise(r => setTimeout(r, 600))
      
      let synthesizedContent = ""
      let mediaCount = 0
      let title = "Новый импорт"
      let mediaFiles: any[] = []
      
      if (jsonInput.trim().startsWith('[')) {
        const parsed = JSON.parse(jsonInput)
        const sorted = [...parsed].sort((a: any, b: any) => 
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        )

        synthesizedContent = sorted.map((m: any) => {
          let text = (m.content || "").replace(/\[\d{2}:\d{2}:\d{2}\] \*\*.*?\*\*: /g, '')
          if (m.attachments && m.attachments.length > 0) {
            m.attachments.forEach((a: any) => {
              const type = a.content_type?.startsWith('video') ? 'video' : 'image'
              text += `\n![${type}](${a.url})\n`
            })
          }
          return text
        }).filter((t: string) => t.trim() !== "").join('\n\n')

        const allAttachments = sorted.flatMap((m: any) => m.attachments || [])
        mediaCount = allAttachments.length
        mediaFiles = allAttachments.map((a: any) => ({
          filename: a.filename,
          url: a.url,
          content_type: a.content_type,
          size: a.size
        }))

        title = "Гайд от " + (sorted[0]?.author?.global_name || sorted[0]?.author?.username || "Community")
      } else {
        synthesizedContent = jsonInput
        const links = jsonInput.match(/https?:\/\/\S+/g)
        mediaCount = links ? links.length : 0
      }
      
      setEditableTitle(title)
      setResult({
        title,
        content: synthesizedContent,
        media_count: mediaCount,
        media_files: mediaFiles,
        status: "Готово к импорту"
      })
    } catch (e) {
      alert("Ошибка обработки: " + e)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateGuide = async () => {
    if (!result) return
    
    setIsImporting(true)
    let finalContent = result.content
    const photos: string[] = []
    const videos: string[] = []
    let failedMedia = 0
    
    try {
      const filesToProcess = result.media_files || []
      setImportProgress({ current: 0, total: filesToProcess.length, status: 'Подготовка файлов...' })
      
      for (let i = 0; i < filesToProcess.length; i++) {
        const file = filesToProcess[i]
        setImportProgress(prev => ({ ...prev, current: i + 1, status: `Загрузка: ${file.filename || 'файл'} (${i + 1}/${filesToProcess.length})` }))
        
        try {
          const uploadRes: any = await apiImportMedia(file.url, `imported/discord/${Date.now()}`)
          
          if (uploadRes && uploadRes.url) {
            finalContent = finalContent.replace(file.url, uploadRes.url)
            
            if (file.content_type?.startsWith('video')) {
              videos.push(uploadRes.url)
            } else {
              photos.push(uploadRes.url)
            }
          }
        } catch (err) {
          failedMedia++
          console.error("Failed to import media file:", file.url, err)
        }
      }
      
      setImportProgress(prev => ({ ...prev, status: 'Сохранение гайда в базу...' }))
      
      // Сохраняем гайд в БД через API
      const guideKey = selectedGuideKey === 'new' ? `imported_${Date.now()}` : selectedGuideKey
      
      // Определяем category_key
      let categoryKey = selectedCategory || 'general'
      if (selectedGuideKey !== 'new') {
        // Для существующего гайда — берём его категорию
        const existing = allGuides.find(g => g.key === selectedGuideKey)
        if (existing) categoryKey = existing.category_key
      }
      
      await apiPut(`/api/admin/guide/${guideKey}`, {
        category_key: categoryKey,
        title: editableTitle,
        text: finalContent,
        photo: photos,
        video: videos,
        document: [],
        sort_order: 0,
      })
      
      setIsImporting(false)
      
      const statusParts = ['✅ Гайд сохранён!']
      if (failedMedia > 0) {
        statusParts.push(`⚠️ ${failedMedia} медиа не загружено (истёкшие ссылки Discord)`)
      }
      
      setResult({
        ...result,
        content: finalContent,
        status: statusParts.join(' | ')
      })
      
      // Обновляем список гайдов
      apiFetch<Guide[]>('/api/admin/guides').then(setAllGuides).catch(() => {})
      
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e)
      alert(`Ошибка при импорте: ${msg}`)
      setIsImporting(false)
    }
  }

  const handleTranslate = async () => {
    if (!result) return
    setIsTranslating(true)
    
    const mediaMap = new Map<string, string>()
    let placeholderIndex = 0
    const protectedRegex = /(!\[(?:image|video)\]\(.*?\)|<a?:[a-zA-Z0-9_]+:\d+>|:[a-zA-Z0-9_]+:|https?:\/\/(?:cdn|media)\.discordapp\.(?:com|net)\/[^\s]+)/g
    
    const safeTextForAi = result.content.replace(protectedRegex, (match: string) => {
      const placeholder = `%%___M_TKN_${placeholderIndex}___%%`
      mediaMap.set(placeholder, match)
      placeholderIndex++
      return placeholder
    })

    try {
      const res = await apiPost<{ translated: string }>('/api/admin/translate', { text: safeTextForAi })
      
      if (res && res.translated) {
        let finalTranslated = res.translated
        mediaMap.forEach((originalMedia, placeholder) => {
          finalTranslated = finalTranslated.replace(placeholder, originalMedia)
        })

        setResult({
          ...result,
          content: finalTranslated,
          status: "Переведено (AI)"
        })
      }
    } catch (e) {
      alert("Ошибка перевода: " + e)
    } finally {
      setIsTranslating(false)
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-xl">
            <Beaker className="size-5 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-black tracking-tight uppercase">Discord Sync Lab</h2>
            <p className="text-[10px] font-bold text-muted-foreground/60 uppercase tracking-widest">
              Тестовая площадка для импорта из Slayerpedia
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        <Card className="xl:col-span-5 p-8 border-none bg-card/40 backdrop-blur-sm space-y-6 shadow-2xl ring-1 ring-white/5">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground/40">
              Ввод: JSON из Discord
            </h3>
            <Button variant="ghost" size="sm" className="h-7 px-3 text-[9px] uppercase font-bold hover:bg-destructive/10 hover:text-destructive" onClick={() => setJsonInput('')}>
              Очистить
            </Button>
          </div>
          <Textarea 
            className="min-h-[550px] font-mono text-[11px] bg-muted/20 border-none focus-visible:ring-primary/20 p-6 rounded-2xl no-scrollbar"
            placeholder='[{"content": "Hello :fire:", "author": {"username": "HalfSquirrel"}}, ...]'
            value={jsonInput}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setJsonInput(e.target.value)}
          />
          <Button 
            className="w-full h-14 rounded-2xl font-black uppercase tracking-widest gap-3 shadow-xl shadow-primary/20 text-xs"
            onClick={runTest}
            disabled={loading}
          >
            {loading ? <RefreshCcw className="size-5 animate-spin" /> : <Send className="size-5" />}
            Запустить синтез
          </Button>
        </Card>

        <Card className="xl:col-span-7 p-8 border-none bg-card/40 backdrop-blur-sm space-y-8 shadow-2xl ring-1 ring-white/5 min-h-[710px] flex flex-col">
          <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground/40">
            Результат синтеза и перевода
          </h3>
          
          {result ? (
            <div className="space-y-6 animate-in zoom-in-95 duration-500 flex-1 flex flex-col">
              {/* Настройки импорта */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-6 bg-primary/5 rounded-[24px] border border-primary/10 shadow-inner">
                <div className="space-y-2">
                  <div className="text-[10px] font-black text-primary uppercase tracking-widest opacity-60">Целевой гайд</div>
                  <select 
                    className="w-full h-11 bg-background/50 border-none rounded-xl px-3 text-xs font-bold focus:ring-2 focus:ring-primary/20 appearance-none cursor-pointer"
                    value={selectedGuideKey}
                    onChange={(e) => setSelectedGuideKey(e.target.value)}
                  >
                    <option value="new">+ Создать новый гайд</option>
                    <optgroup label="Существующие гайды (Заменить)">
                      {allGuides.map(g => (
                        <option key={g.key} value={g.key}>{g.title}</option>
                      ))}
                    </optgroup>
                  </select>
                </div>

                {selectedGuideKey === 'new' && categories.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-[10px] font-black text-primary uppercase tracking-widest opacity-60">Категория</div>
                    <select 
                      className="w-full h-11 bg-background/50 border-none rounded-xl px-3 text-xs font-bold focus:ring-2 focus:ring-primary/20 appearance-none cursor-pointer"
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      {categories.map(c => (
                        <option key={c.key} value={c.key}>{c.title}</option>
                      ))}
                    </select>
                  </div>
                )}

                <div className="space-y-2">
                  <div className="text-[10px] font-black text-primary uppercase tracking-widest opacity-60">Название гайда</div>
                  <Input 
                    className="h-11 bg-background/50 border-none font-bold text-sm focus-visible:ring-primary/20 rounded-xl"
                    value={editableTitle}
                    onChange={(e) => setEditableTitle(e.target.value)}
                    placeholder="Введите название..."
                  />
                </div>
                
                <div className="col-span-full pt-2 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Database className="size-3 text-primary/40" />
                    <span className="text-[9px] font-bold text-muted-foreground/40 uppercase">
                      {selectedGuideKey === 'new' ? 'Будет создан новый объект в базе' : `Обновит контент гайда: ${selectedGuideKey}`}
                    </span>
                  </div>
                  <div className="px-3 py-1 bg-primary text-primary-foreground rounded-lg text-[9px] font-black uppercase tracking-widest">
                    {result.status}
                  </div>
                </div>
              </div>

              <div className="flex-1 p-8 bg-muted/20 rounded-[32px] border border-white/5 space-y-4 shadow-inner relative overflow-hidden">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-[10px] font-black text-muted-foreground/40 uppercase tracking-widest">Содержимое гайда</div>
                  <div className="px-3 py-1 bg-muted/40 rounded-full text-[9px] font-bold text-primary/60 border border-primary/5">{result.media_count} медиа-файлов</div>
                </div>
                <div className="max-h-[400px] overflow-y-auto no-scrollbar pr-2">
                  <FormattedContent text={result.content} />
                </div>
              </div>

              {result.media_files && result.media_files.length > 0 && (
                <div className="space-y-2">
                  <div className="text-[10px] font-black text-muted-foreground/40 uppercase">Найденные медиа (Временные ссылки)</div>
                  <div className="grid grid-cols-1 gap-2">
                    {result.media_files.slice(0, 3).map((f: any, i: number) => (
                      <div key={i} className="flex items-center justify-between p-2 bg-muted/10 rounded-xl text-[10px] font-mono truncate">
                        <span className="truncate flex-1 pr-2">{f.filename}</span>
                        <span className="text-primary/40 shrink-0">{f.content_type}</span>
                      </div>
                    ))}
                    {result.media_files.length > 3 && (
                      <div className="text-[9px] text-center text-muted-foreground italic">и еще {result.media_files.length - 3} файла...</div>
                    )}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <Button 
                  className="h-14 rounded-2xl bg-primary shadow-xl shadow-primary/20 text-md font-black uppercase tracking-wider group"
                  onClick={handleCreateGuide}
                  disabled={isImporting}
                >
                  {isImporting ? (
                    <div className="flex items-center gap-2">
                      <RefreshCcw className="size-4 animate-spin" />
                      <span>{importProgress.current}/{importProgress.total}</span>
                    </div>
                  ) : (
                    <>
                      <Send className="mr-2 size-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                      Импорт медиа и создать
                    </>
                  )}
                </Button>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="secondary" 
                    className="flex-1 rounded-2xl text-xs gap-2 bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 border border-indigo-500/20"
                    onClick={handleTranslate}
                    disabled={isTranslating}
                  >
                    {isTranslating ? <RefreshCcw className="size-3.5 animate-spin" /> : <Globe className="size-3.5" />}
                    Перевести (AI)
                  </Button>
                  <Button 
                    variant="secondary" 
                    className="flex-1 rounded-2xl text-xs gap-2"
                    onClick={() => {
                      navigator.clipboard.writeText(result.content)
                      alert("Текст скопирован!")
                    }}
                  >
                    <Copy className="size-3.5" />
                    Копировать текст
                  </Button>
                </div>
              </div>

              {isImporting && (
                <div className="p-4 bg-primary/10 rounded-2xl border border-primary/20 animate-in slide-in-from-bottom-2">
                  <div className="text-[10px] font-black text-primary uppercase tracking-[0.2em] mb-1">Процесс автоматизации</div>
                  <div className="text-xs font-bold text-foreground/80">{importProgress.status}</div>
                  <div className="mt-2 h-1 w-full bg-primary/20 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-300" 
                      style={{ width: `${(importProgress.current / importProgress.total) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-[350px] text-muted-foreground/20 italic text-sm">
              <RefreshCcw className="size-10 mb-4 opacity-10" />
              Ожидание данных...
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}

// Компонент для отрисовки контента с иконками вынесен наружу для стабильности хуков
const FormattedContent = ({ text }: { text: string }) => {
  const parts = useMemo(() => {
    // Ищем <a:name:id>, <:name:id>, :name:, ![type](url), и прямые ссылки Discord
    return text.split(/(<a?:[a-zA-Z0-9_]+:\d+>|:[a-zA-Z0-9_]+:|!\[(?:image|video)\]\(.*?\)|https?:\/\/(?:cdn|media)\.discordapp\.(?:com|net)\/attachments\/\d+\/\d+\/[\w.-]+(?:\?[\w=&.%-]+)?)/g)
  }, [text])

  return (
    <div className="text-sm leading-relaxed whitespace-pre-wrap opacity-90">
      {parts.map((part, i) => {
        // 1. Обработка Discord эмодзи
        const emojiMatch = part.match(/<(a?):([a-zA-Z0-9_]+):(\d+)>/) || part.match(/^:([a-zA-Z0-9_]+):$/)
        if (emojiMatch) {
          let name = ''
          let url = null
          
          if (emojiMatch.length === 4) {
            const isAnimated = emojiMatch[1] === 'a'
            name = emojiMatch[2]
            const id = emojiMatch[3]
            url = getGameIconUrl(name)
            if (!url) {
              url = apiGetProxyUrl(`https://cdn.discordapp.com/emojis/${id}.${isAnimated ? 'gif' : 'webp'}?size=48`)
            }
          } else {
            name = emojiMatch[1]
            url = getGameIconUrl(name)
          }

          if (url) {
            return (
              <img 
                key={i} 
                src={url} 
                alt={name} 
                className="inline-block size-5 mx-0.5 -mt-1 rounded-sm align-middle hover:scale-150 transition-transform cursor-help object-contain"
                title={name}
              />
            )
          }
        }

        // 2. Обработка тегов ![image](url) или ![video](url)
        const mediaMatch = part.match(/!\[(image|video)\]\((.*?)\)/)
        if (mediaMatch) {
          const type = mediaMatch[1]
          const rawUrl = mediaMatch[2]
          const proxiedUrl = apiGetProxyUrl(rawUrl)
          
          return type === 'image' ? (
            <img 
              key={i} 
              src={proxiedUrl} 
              alt="Preview" 
              className="my-4 rounded-2xl w-full object-cover shadow-lg border border-white/10" 
            />
          ) : (
            <video 
              key={i} 
              src={proxiedUrl} 
              controls 
              className="my-4 rounded-2xl w-full shadow-lg border border-white/10" 
            />
          )
        }

        // 3. Обработка прямых ссылок Discord (если они не попали в теги)
        if (part.startsWith('http') && (part.includes('discordapp.com') || part.includes('discordapp.net'))) {
          const proxiedUrl = apiGetProxyUrl(part)
          const isVideo = part.toLowerCase().split('?')[0].endsWith('.mp4') || part.toLowerCase().split('?')[0].endsWith('.mov')
          
          return isVideo ? (
            <video 
              key={i} 
              src={proxiedUrl} 
              controls 
              className="my-4 rounded-2xl w-full shadow-lg border border-white/10" 
            />
          ) : (
            <img 
              key={i} 
              src={proxiedUrl} 
              alt="Direct link preview" 
              className="my-4 rounded-2xl w-full object-cover shadow-lg border border-white/10" 
            />
          )
        }

        return <span key={i}>{part}</span>
      })}
    </div>
  )
}
