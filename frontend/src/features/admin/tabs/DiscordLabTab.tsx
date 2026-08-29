import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  apiAddDiscordSyncChannel,
  apiBackfillAllDiscordChannels,
  apiBackfillDiscordChannel,
  apiClearSyncedDiscordGuides,
  apiDeleteSyncedDiscordGuide,
  apiFetch,
  apiGetDiscordSyncChannels,
  apiGetDiscordSyncStatus,
  apiGetProxyUrl,
  apiGetSyncedDiscordGuides,
  apiImportDiscordLink,
  apiImportMedia,
  apiPost,
  apiPut,
  apiRemoveDiscordSyncChannel,
  apiStartDiscordSync,
  apiStopDiscordSync,
} from '@/lib/api'
import { getGameIconUrl } from '@/lib/gameIcons'
import {
  Beaker,
  Clock,
  Copy,
  Database,
  ExternalLink,
  Globe,
  History,
  Pause,
  Play,
  Plus,
  RefreshCcw,
  RefreshCw,
  Search,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  Trash2,
} from '@/lib/icons'
import type { Category, Guide } from '@/lib/types'
import { useQuery } from '@tanstack/react-query'
import { type ChangeEvent, type FC, useEffect, useMemo, useState } from 'react'

interface DiscordAttachment {
  filename: string
  url: string
  content_type?: string
  size: number
}

interface DiscordMessage {
  content: string
  author: {
    username: string
    global_name?: string
  }
  timestamp: string
  attachments?: DiscordAttachment[]
  channel_id?: string
}

// TODO: Укажите здесь реальные ID каналов Discord и соответствующие им ключи категорий
const CHANNEL_TO_CATEGORY: Record<string, string> = {
  '123456789012345678': 'builds',
  '987654321098765432': 'guides',
  '111111111111111111': 'news',
}

interface SynthesisResult {
  title: string
  content: string
  media_count: number
  media_files: DiscordAttachment[]
  status: string
}

export const DiscordLabTab: FC = () => {
  const [jsonInput, setJsonInput] = useState('')
  const [result, setResult] = useState<SynthesisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [isImporting, setIsImporting] = useState(false)
  const [isTranslating, setIsTranslating] = useState(false)
  const [importProgress, setImportProgress] = useState({ current: 0, total: 0, status: '' })
  const [editableTitle, setEditableTitle] = useState('')
  const [selectedGuideKey, setSelectedGuideKey] = useState<string>('new')
  const [allGuides, setAllGuides] = useState<Guide[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')

  // Worker & Channels Sync State
  const [workerToken, setWorkerToken] = useState('')
  const [workerStatus, setWorkerStatus] = useState<{
    running: boolean
    channels_count: number
    has_token: boolean
    has_saved_token?: boolean
    token_preview?: string | null
  }>({
    running: false,
    channels_count: 0,
    has_token: false,
    has_saved_token: false,
    token_preview: null,
  })

  const handleClearToken = async () => {
    try {
      await apiPost('/api/admin/discord-sync/clear-token', {})
      setWorkerToken('')
      fetchSyncState()
      alert('Токен отвязан от вашей учетной записи')
    } catch (e: unknown) {
      alert('Ошибка: ' + ((e as Error).message || e))
    }
  }

  const handleStartWithSavedToken = async () => {
    setWorkerLoading(true)
    try {
      const res = await apiStartDiscordSync(workerToken.trim() || '')
      alert(res.message || 'Слушатель запущен')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка запуска: ' + ((e as Error).message || e))
    } finally {
      setWorkerLoading(false)
    }
  }
  const [syncChannels, setSyncChannels] = useState<
    Array<{
      channel_id: string
      channel_name?: string
      category_key: string
      auto_translate: boolean
      is_active: boolean
    }>
  >([])
  const [syncedGuides, setSyncedGuides] = useState<
    Array<{
      id: number
      discord_message_id: string
      discord_channel_id: string
      guide_key: string
      author_tag: string
      created_at: string
      title: string
      category_key: string
      views: number
    }>
  >([])
  const [newChannelId, setNewChannelId] = useState('')
  const [newChannelName, setNewChannelName] = useState('')
  const [newChannelCat, setNewChannelCat] = useState('')
  const [workerLoading, setWorkerLoading] = useState(false)
  const [backfillingId, setBackfillingId] = useState<string | null>(null)

  // TanStack Query optimized polling: 10s interval, automatically paused when tab is hidden
  const { data: syncStateData, refetch: refetchSyncState } = useQuery({
    queryKey: ['discord-lab-sync-state'],
    queryFn: async () => {
      const st = await apiGetDiscordSyncStatus()
      const chs = await apiGetDiscordSyncChannels()
      const sg = await apiGetSyncedDiscordGuides()
      return { status: st, channels: chs.channels || [], synced_guides: sg.synced_guides || [] }
    },
    refetchInterval: (query) => {
      if (document.visibilityState === 'hidden') return false
      return query.state.data?.status?.running ? 10_000 : 30_000
    },
    refetchIntervalInBackground: false,
    staleTime: 5_000,
    gcTime: 10 * 60_000,
  })

  useEffect(() => {
    if (syncStateData) {
      setWorkerStatus(syncStateData.status)
      setSyncChannels(syncStateData.channels)
      setSyncedGuides(syncStateData.synced_guides)
    }
  }, [syncStateData])

  const fetchSyncState = () => {
    refetchSyncState()
  }

  const [isBackfillingAll, setIsBackfillingAll] = useState(false)

  const handleBackfillChannel = async (channelId: string) => {
    setBackfillingId(channelId)
    try {
      const res = await apiBackfillDiscordChannel(channelId)
      alert(res.message || 'Сканирование истории канала запущено')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка сканирования: ' + ((e as Error).message || e))
    } finally {
      setBackfillingId(null)
    }
  }

  const handleBackfillAllChannels = async () => {
    setIsBackfillingAll(true)
    try {
      const res = await apiBackfillAllDiscordChannels()
      alert(res.message || 'Сканирование всех каналов завершено')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка сканирования: ' + ((e as Error).message || e))
    } finally {
      setIsBackfillingAll(false)
    }
  }

  const [importLinkUrl, setImportLinkUrl] = useState('')
  const [isImportingLink, setIsImportingLink] = useState(false)

  const handleImportLink = async () => {
    if (!importLinkUrl.trim()) return
    setIsImportingLink(true)
    try {
      const res = await apiImportDiscordLink(importLinkUrl.trim())
      alert(res.message || 'Импорт по ссылке успешно выполнен!')
      setImportLinkUrl('')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка импорта: ' + ((e as Error).message || e))
    } finally {
      setIsImportingLink(false)
    }
  }

  const [syncedSearch, setSyncedSearch] = useState('')
  const [deletingSyncedId, setDeletingSyncedId] = useState<number | null>(null)

  const handleDeleteSyncedGuide = async (id: number, deleteGuide: boolean) => {
    const confirmMsg = deleteGuide
      ? 'Вы уверены, что хотите удалить эту запись из очереди И сам гайд с сайта?'
      : 'Удалить эту запись из журнала очереди?'
    if (!window.confirm(confirmMsg)) return

    setDeletingSyncedId(id)
    try {
      const res = await apiDeleteSyncedDiscordGuide(id, deleteGuide)
      alert(res.message || 'Запись удалена из очереди')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка удаления: ' + ((e as Error).message || e))
    } finally {
      setDeletingSyncedId(null)
    }
  }

  const handleClearSyncedHistory = async (deleteGuides: boolean) => {
    const confirmMsg = deleteGuides
      ? '⚠️ ВНИМАНИЕ! Вы уверены, что хотите очистить ВСЮ очередь И УДАЛИТЬ все соответствующие гайды с сайта?'
      : 'Очистить историю журнала очереди?'
    if (!window.confirm(confirmMsg)) return

    try {
      const res = await apiClearSyncedDiscordGuides(deleteGuides)
      alert(res.message || 'Журнал очереди очищен')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка очистки: ' + ((e as Error).message || e))
    }
  }

  const filteredSyncedGuides = useMemo(() => {
    if (!syncedSearch.trim()) return syncedGuides
    const q = syncedSearch.toLowerCase()
    return syncedGuides.filter(
      (g) =>
        (g.title || '').toLowerCase().includes(q) ||
        (g.author_tag || '').toLowerCase().includes(q) ||
        (g.category_key || '').toLowerCase().includes(q) ||
        (g.discord_message_id || '').includes(q) ||
        (g.discord_channel_id || '').includes(q)
    )
  }, [syncedGuides, syncedSearch])

  useEffect(() => {
    apiFetch<Guide[]>('/api/admin/guides')
      .then(setAllGuides)
      .catch(() => {})
    apiFetch<Category[]>('/api/admin/categories')
      .then((cats) => {
        setCategories(cats)
        if (cats.length > 0) {
          setSelectedCategory(cats[0].key)
          setNewChannelCat(cats[0].key)
        }
      })
      .catch(() => {})
    fetchSyncState()
  }, [])

  const runTest = async () => {
    if (!jsonInput.trim()) return
    setLoading(true)
    try {
      await new Promise((r) => setTimeout(r, 600))

      let synthesizedContent = ''
      let mediaCount = 0
      let title = 'Новый импорт'
      let mediaFiles: DiscordAttachment[] = []

      if (jsonInput.trim().startsWith('[')) {
        const parsed = JSON.parse(jsonInput) as DiscordMessage[]
        const sorted = [...parsed].sort(
          (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        )

        const firstMsgChannel = sorted.find((m) => m.channel_id)?.channel_id
        if (firstMsgChannel && CHANNEL_TO_CATEGORY[firstMsgChannel]) {
          const matchedCategory = CHANNEL_TO_CATEGORY[firstMsgChannel]
          // Проверяем, существует ли такая категория
          if (categories.some((c) => c.key === matchedCategory)) {
            setSelectedCategory(matchedCategory)
          }
        }

        synthesizedContent = sorted
          .map((m) => {
            let text = (m.content || '').replace(/\[\d{2}:\d{2}:\d{2}\] \*\*.*?\*\*: /g, '')
            if (m.attachments && m.attachments.length > 0) {
              for (const a of m.attachments) {
                const type = a.content_type?.startsWith('video') ? 'video' : 'image'
                text += `\n![${type}](${a.url})\n`
              }
            }
            return text
          })
          .filter((t: string) => t.trim() !== '')
          .join('\n\n')

        const allAttachments = sorted.flatMap((m) => m.attachments || [])
        mediaCount = allAttachments.length
        mediaFiles = allAttachments.map((a) => ({
          filename: a.filename,
          url: a.url,
          content_type: a.content_type,
          size: a.size,
        }))

        title =
          'Гайд от ' +
          (sorted[0]?.author?.global_name || sorted[0]?.author?.username || 'Community')
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
        status: 'Готово к импорту',
      })
    } catch (e) {
      alert('Ошибка обработки: ' + e)
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
      setImportProgress({
        current: 0,
        total: filesToProcess.length,
        status: 'Подготовка файлов...',
      })

      for (let i = 0; i < filesToProcess.length; i++) {
        const file = filesToProcess[i]
        setImportProgress((prev) => ({
          ...prev,
          current: i + 1,
          status: `Загрузка: ${file.filename || 'файл'} (${i + 1}/${filesToProcess.length})`,
        }))

        try {
          const uploadRes = (await apiImportMedia(file.url, `imported/discord/${Date.now()}`)) as {
            url?: string
          }

          if (uploadRes?.url) {
            finalContent = finalContent.replace(file.url, uploadRes.url)

            if (file.content_type?.startsWith('video')) {
              videos.push(uploadRes.url)
            } else {
              photos.push(uploadRes.url)
            }
          }
        } catch (err) {
          failedMedia++
          console.error('Failed to import media file:', file.url, err)
        }
      }

      setImportProgress((prev) => ({ ...prev, status: 'Сохранение гайда в базу...' }))

      // Сохраняем гайд в БД через API
      const slugify = (text: string) => {
        return text
          .toString()
          .toLowerCase()
          .trim()
          .replace(/\s+/g, '_') // Пробелы в _
          .replace(/[^\w-]+/g, '') // Удаляем всё кроме букв, цифр, - и _
          .replace(/--+/g, '_') // Двойные -- в _
          .substring(0, 60) // Лимит бэкенда 64 символа
      }

      const guideKey =
        selectedGuideKey === 'new'
          ? `${slugify(editableTitle)}_${Date.now().toString().slice(-4)}`
          : selectedGuideKey

      // Определяем category_key
      let categoryKey = selectedCategory || 'general'
      if (selectedGuideKey !== 'new') {
        // Для существующего гайда — берём его категорию
        const existing = allGuides.find((g) => g.key === selectedGuideKey)
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
        status: statusParts.join(' | '),
      })

      // Обновляем список гайдов
      apiFetch<Guide[]>('/api/admin/guides')
        .then(setAllGuides)
        .catch(() => {})
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
    const protectedRegex =
      /(!\[(?:image|video)\]\(.*?\)|<a?:[a-zA-Z0-9_]+:\d+>|:[a-zA-Z0-9_]+:|https?:\/\/(?:cdn|media)\.discordapp\.(?:com|net)\/[^\s]+)/g

    const safeTextForAi = result.content.replace(protectedRegex, (match: string) => {
      const placeholder = `%%___M_TKN_${placeholderIndex}___%%`
      mediaMap.set(placeholder, match)
      placeholderIndex++
      return placeholder
    })

    try {
      const res = await apiPost<{ translated: string }>('/api/admin/translate', {
        text: safeTextForAi,
      })

      if (res?.translated) {
        let finalTranslated = res.translated
        mediaMap.forEach((originalMedia, placeholder) => {
          finalTranslated = finalTranslated.replace(placeholder, originalMedia)
        })

        setResult({
          ...result,
          content: finalTranslated,
          status: 'Переведено (AI)',
        })
      }
    } catch (e) {
      alert('Ошибка перевода: ' + e)
    } finally {
      setIsTranslating(false)
    }
  }

  const handleStartWorker = async () => {
    if (!workerToken.trim()) return alert('Введите Discord User Token')
    setWorkerLoading(true)
    try {
      const res = await apiStartDiscordSync(workerToken.trim())
      alert(res.message || 'Слушатель запущен')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка запуска: ' + ((e as Error).message || e))
    } finally {
      setWorkerLoading(false)
    }
  }

  const handleStopWorker = async () => {
    setWorkerLoading(true)
    try {
      const res = await apiStopDiscordSync()
      alert(res.message || 'Слушатель остановлен')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка: ' + ((e as Error).message || e))
    } finally {
      setWorkerLoading(false)
    }
  }

  const handleAddChannel = async () => {
    if (!newChannelId.trim()) return alert('Укажите ID канала')
    try {
      await apiAddDiscordSyncChannel({
        channel_id: newChannelId.trim(),
        channel_name: newChannelName.trim() || undefined,
        category_key: newChannelCat,
        auto_translate: true,
      })
      setNewChannelId('')
      setNewChannelName('')
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка добавления канала: ' + ((e as Error).message || e))
    }
  }

  const handleRemoveChannel = async (channelId: string) => {
    try {
      await apiRemoveDiscordSyncChannel(channelId)
      fetchSyncState()
    } catch (e: unknown) {
      alert('Ошибка удаления: ' + ((e as Error).message || e))
    }
  }

  return (
    <div className="w-full space-y-8 animate-in fade-in duration-500">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 bg-gradient-to-r from-violet-950/40 via-card/60 to-indigo-950/40 backdrop-blur-xl border border-primary/20 rounded-3xl shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-2xl text-white shadow-lg shadow-violet-500/25 border border-white/10">
            <Beaker className="size-6" />
          </div>
          <div>
            <h2 className="text-2xl font-black tracking-tight uppercase font-heading text-foreground">
              Discord Sync Lab & Live Gateway Worker
            </h2>
            <p className="text-xs font-bold text-primary/80 uppercase tracking-widest mt-0.5">
              Автоматическая бессерверная синхронизация, ИИ-выжимка и импорт гайдов
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 bg-background/60 rounded-2xl border border-white/10 backdrop-blur-md">
            <div
              className={`size-2.5 rounded-full ${workerStatus.running ? 'bg-emerald-400 animate-ping' : 'bg-rose-500'}`}
            />
            <span className="text-xs font-black uppercase tracking-wider text-foreground">
              {workerStatus.running ? 'Шлюз Активен' : 'Шлюз Остановлен'}
            </span>
          </div>
        </div>
      </div>

      {/* Interactive Visual Pipeline Stepper */}
      <Card className="p-6 border border-primary/20 bg-gradient-to-br from-card/90 via-card/60 to-card/90 backdrop-blur-xl rounded-3xl space-y-5 shadow-2xl">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-black uppercase tracking-widest text-primary font-heading">
            ⚡ Этапы Конвейера Авто-Синхронизации (Pipeline Flow)
          </h3>
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
            5 Интерактивных Стадий
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {[
            {
              step: '1',
              title: '1. Gateway Listener',
              desc: 'Пассивный WebSocket',
              status: workerStatus.running ? 'active' : 'idle',
              icon: ShieldCheck,
            },
            {
              step: '2',
              title: '2. SHA-256 Diffing',
              desc: 'Сверка версий',
              status: workerStatus.running ? 'active' : 'idle',
              icon: RefreshCw,
            },
            {
              step: '3',
              title: '3. ИИ-Перевод',
              desc: 'EN ➔ RU + TL;DR',
              status: workerStatus.running ? 'active' : 'idle',
              icon: Globe,
            },
            {
              step: '4',
              title: '4. Кэш Медиа',
              desc: 'Сохранение фото',
              status: workerStatus.running ? 'active' : 'idle',
              icon: Database,
            },
            {
              step: '5',
              title: '5. Публикация',
              desc: 'Обновление в БД',
              status: workerStatus.running ? 'active' : 'idle',
              icon: Sparkles,
            },
          ].map((s) => (
            <div
              key={s.step}
              className={`p-3.5 rounded-2xl border transition-all ${
                s.status === 'active'
                  ? 'bg-primary/10 border-primary/30 text-foreground shadow-md shadow-primary/5'
                  : 'bg-background/40 border-white/5 text-muted-foreground/60'
              }`}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <s.icon
                  className={`size-4 ${s.status === 'active' ? 'text-primary animate-pulse' : 'text-muted-foreground/40'}`}
                />
                <span className="text-xs font-black uppercase tracking-wide font-heading">
                  {s.title}
                </span>
              </div>
              <p className="text-[10px] font-medium text-muted-foreground">{s.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Stealth Discord Gateway Worker Control Card */}
      <Card className="p-6 border border-primary/20 bg-gradient-to-br from-card/90 via-card/50 to-card/90 backdrop-blur-xl rounded-3xl space-y-6 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-2xl text-white shadow-xl shadow-violet-500/25 border border-white/10">
              <ShieldCheck className="size-6" />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h3 className="text-base font-black uppercase font-heading text-foreground">
                  Бесшумный Авто-Синхронизатор Discord
                </h3>
                <span
                  className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${
                    workerStatus.running
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-lg shadow-emerald-950/40'
                      : 'bg-muted/60 text-muted-foreground border border-white/10'
                  }`}
                >
                  {workerStatus.running
                    ? '🟢 Активен (Слушает в реальном времени)'
                    : '🔴 Остановлен'}
                </span>
              </div>
              <p className="text-xs text-muted-foreground/80 font-medium mt-1">
                Пассивный WebSocket-слушатель чужих каналов Discord с автопереводом EN ➔ RU и
                локальным кэшированием медиа.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            {workerStatus.running ? (
              <Button
                variant="destructive"
                className="h-11 px-6 rounded-2xl font-black text-xs uppercase tracking-wider gap-2 cursor-pointer w-full sm:w-auto shadow-xl shadow-rose-950/40 border border-rose-500/30"
                disabled={workerLoading}
                onClick={handleStopWorker}
              >
                <Pause className="size-4" /> Остановить
              </Button>
            ) : workerStatus.has_saved_token ? (
              <Button
                variant="default"
                className="h-11 px-6 rounded-2xl font-black text-xs uppercase tracking-wider gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white cursor-pointer w-full sm:w-auto shadow-xl shadow-emerald-950/40 border border-white/10"
                disabled={workerLoading}
                onClick={handleStartWithSavedToken}
              >
                <Play className="size-4" /> Запустить (Авто-токен)
              </Button>
            ) : (
              <Button
                variant="default"
                className="h-11 px-6 rounded-2xl font-black text-xs uppercase tracking-wider gap-2 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white cursor-pointer w-full sm:w-auto shadow-xl shadow-violet-950/40 border border-white/10"
                disabled={workerLoading || !workerToken.trim()}
                onClick={handleStartWorker}
              >
                <Play className="size-4" /> Запустить и Закрепить
              </Button>
            )}
          </div>
        </div>

        {workerStatus.has_saved_token && (
          <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <ShieldCheck className="size-5 text-emerald-400 shrink-0" />
              <div>
                <div className="font-black uppercase tracking-wider text-emerald-300">
                  🔒 Токен зафиксирован за вашей учётной записью
                </div>
                <div className="text-[11px] text-muted-foreground mt-0.5">
                  Активный токен:{' '}
                  <code className="font-mono text-primary bg-primary/10 px-2 py-0.5 rounded-md">
                    {workerStatus.token_preview || '••••••••'}
                  </code>
                  . Вам больше не нужно вводить его вручную!
                </div>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              className="h-8 px-3 text-[11px] font-bold text-rose-400 border-rose-500/30 hover:bg-rose-500/20 rounded-xl cursor-pointer"
              onClick={handleClearToken}
            >
              Отвязать токен
            </Button>
          </div>
        )}

        {!workerStatus.running && (
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-end bg-background/60 p-5 rounded-2xl border border-white/10 backdrop-blur-md">
            <div className="sm:col-span-9 space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-primary/80 ml-1 font-heading">
                {workerStatus.has_saved_token
                  ? 'Изменить зафиксированный токен Discord'
                  : 'Ввести токен Discord для привязки'}
              </label>
              <Input
                type="password"
                placeholder={
                  workerStatus.has_saved_token
                    ? 'Введите новый токен для обновления...'
                    : 'Вставьте токен вашего аккаунта-читателя...'
                }
                className="h-11 rounded-2xl bg-background/80 border border-white/10 font-mono text-xs text-foreground focus-visible:ring-primary/40 focus-visible:border-primary/50"
                value={workerToken}
                onChange={(e) => setWorkerToken(e.target.value)}
              />
            </div>
            <div className="sm:col-span-3">
              <Button
                className="h-11 w-full rounded-2xl text-xs font-black uppercase tracking-wider bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white border border-white/10 shadow-lg cursor-pointer"
                onClick={handleStartWorker}
                disabled={!workerToken.trim() || workerLoading}
              >
                Сохранить и Старт
              </Button>
            </div>
          </div>
        )}

        {/* Instant Import by Discord Link */}
        <div className="bg-gradient-to-r from-violet-950/30 via-background/60 to-indigo-950/30 p-5 rounded-2xl border border-violet-500/20 backdrop-blur-md space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-black uppercase tracking-wider text-violet-300 font-heading flex items-center gap-2">
              <ExternalLink className="size-4 text-violet-400" />🚀 Мгновенный Импорт по Ссылке на
              Пост / Сообщение Discord
            </h4>
            <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest">
              1-Click Link Import
            </span>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Input
              placeholder="Вставьте ссылку на пост Discord (например: https://discord.com/channels/1066.../1266...)"
              className="h-11 flex-1 rounded-xl bg-background/80 border border-violet-500/30 text-xs font-mono text-foreground placeholder:text-muted-foreground/50"
              value={importLinkUrl}
              onChange={(e) => setImportLinkUrl(e.target.value)}
            />
            <Button
              onClick={handleImportLink}
              disabled={!importLinkUrl.trim() || isImportingLink}
              className="h-11 px-6 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-xs gap-2 cursor-pointer shadow-lg shadow-violet-500/20"
            >
              <Sparkles className={`size-4 ${isImportingLink ? 'animate-spin' : ''}`} />
              {isImportingLink ? 'Импортирую...' : 'Импортировать Гайд'}
            </Button>
          </div>
        </div>

        {/* Channel Sync Rules Table & Add Form */}
        <div className="space-y-4 pt-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <h4 className="text-xs font-black uppercase tracking-wider text-foreground font-heading">
              Отслеживаемые каналы Discord ({syncChannels.length})
            </h4>
            {syncChannels.length > 0 && (
              <Button
                size="sm"
                variant="outline"
                disabled={isBackfillingAll}
                onClick={handleBackfillAllChannels}
                className="h-8 rounded-xl border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 text-xs font-bold gap-2 cursor-pointer transition-all"
              >
                <Sparkles className={`size-3.5 ${isBackfillingAll ? 'animate-spin' : ''}`} />
                {isBackfillingAll
                  ? 'Сканирование всех каналов...'
                  : `⚡ Сканировать ВСЕ каналы (${syncChannels.length})`}
              </Button>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-center bg-background/50 p-4 rounded-2xl border border-white/10 backdrop-blur-md">
            <div className="sm:col-span-4">
              <Input
                placeholder="ID канала (например 123456...)"
                className="h-10 rounded-xl bg-background/80 border border-white/10 text-xs font-mono text-foreground"
                value={newChannelId}
                onChange={(e) => setNewChannelId(e.target.value)}
              />
            </div>
            <div className="sm:col-span-4">
              <Input
                placeholder="Название канала (опционально)"
                className="h-10 rounded-xl bg-background/80 border border-white/10 text-xs text-foreground"
                value={newChannelName}
                onChange={(e) => setNewChannelName(e.target.value)}
              />
            </div>
            <div className="sm:col-span-3">
              <select
                className="h-10 w-full rounded-xl bg-background border border-white/10 px-3 text-xs font-bold text-foreground cursor-pointer"
                value={newChannelCat}
                onChange={(e) => setNewChannelCat(e.target.value)}
              >
                {categories.map((c) => (
                  <option key={c.key} value={c.key} className="bg-card text-foreground">
                    {c.title}
                  </option>
                ))}
              </select>
            </div>
            <div className="sm:col-span-1">
              <Button
                size="icon"
                className="h-10 w-full rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white cursor-pointer shadow-md border border-white/10"
                onClick={handleAddChannel}
                title="Добавить канал"
              >
                <Plus className="size-4" />
              </Button>
            </div>
          </div>

          {syncChannels.length > 0 && (
            <div className="divide-y divide-white/10 rounded-2xl border border-white/10 overflow-hidden bg-background/40 backdrop-blur-md">
              {syncChannels.map((ch) => (
                <div
                  key={ch.channel_id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-3 text-xs"
                >
                  <div className="flex items-center gap-3">
                    <div className="font-mono font-bold text-primary px-3 py-1 bg-primary/10 rounded-xl border border-primary/20">
                      #{ch.channel_id}
                    </div>
                    <div>
                      <div className="font-bold text-foreground text-sm">
                        {ch.channel_name || 'Канал Discord'}
                      </div>
                      <div className="text-[11px] text-muted-foreground mt-0.5">
                        Категория на сайте:{' '}
                        <span className="font-bold text-primary">{ch.category_key}</span> •
                        Автоперевод EN➔RU
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-9 px-4 text-xs font-bold gap-2 rounded-xl border-primary/30 text-primary hover:bg-primary/20 cursor-pointer"
                      disabled={backfillingId === ch.channel_id || !workerStatus.running}
                      onClick={() => handleBackfillChannel(ch.channel_id)}
                      title="Сканировать историю этого канала и занести гайды в очередь"
                    >
                      <RefreshCw
                        className={`size-3.5 ${backfillingId === ch.channel_id ? 'animate-spin' : ''}`}
                      />
                      {backfillingId === ch.channel_id ? 'Сканирование...' : 'Сканировать очередь'}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="size-9 text-destructive hover:bg-destructive/20 rounded-xl cursor-pointer"
                      onClick={() => handleRemoveChannel(ch.channel_id)}
                      title="Удалить привязку"
                    >
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Sync Activity Feed & History Table */}
        <div className="space-y-4 pt-4 border-t border-white/10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <History className="size-4 text-primary" />
              <h4 className="text-xs font-black uppercase tracking-wider text-foreground font-heading">
                Журнал очереди и импорта ({syncedGuides.length})
              </h4>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 text-[11px] uppercase font-black gap-1.5 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-xl cursor-pointer"
                onClick={fetchSyncState}
              >
                <RefreshCw className="size-3.5" /> Обновить лог
              </Button>
              {syncedGuides.length > 0 && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-[11px] font-bold text-rose-400 border-rose-500/30 hover:bg-rose-500/20 rounded-xl cursor-pointer"
                    onClick={() => handleClearSyncedHistory(false)}
                    title="Удалит историю из очереди, сохранив гайды на сайте"
                  >
                    <Trash2 className="size-3.5 mr-1" /> Очистить лог
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-[11px] font-bold text-rose-400 bg-rose-500/10 border-rose-500/40 hover:bg-rose-500/30 rounded-xl cursor-pointer"
                    onClick={() => handleClearSyncedHistory(true)}
                    title="Удалит историю И ВСЕ ИМПОРТИРОВАННЫЕ ГАЙДЫ с сайта"
                  >
                    <Trash2 className="size-3.5 mr-1" /> Очистить лог + Гайды
                  </Button>
                </>
              )}
            </div>
          </div>

          {syncedGuides.length > 0 && (
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
              <Input
                placeholder="Поиск по журналу очереди (название, автор, ID)..."
                className="h-10 pl-10 rounded-xl bg-background/60 border border-white/10 text-xs font-medium text-foreground placeholder:text-muted-foreground/60"
                value={syncedSearch}
                onChange={(e) => setSyncedSearch(e.target.value)}
              />
            </div>
          )}

          {filteredSyncedGuides.length === 0 ? (
            <div className="p-10 text-center bg-background/30 rounded-3xl border border-dashed border-white/10 space-y-3">
              <Sparkles className="size-10 text-primary/40 mx-auto animate-bounce" />
              <p className="text-sm font-bold text-foreground">
                {syncedGuides.length === 0
                  ? 'История очереди пока пуста'
                  : 'Ничего не найдено по вашему запросу'}
              </p>
              <p className="text-xs text-muted-foreground max-w-md mx-auto">
                {syncedGuides.length === 0
                  ? 'Запустите слушатель или нажмите «Сканировать очередь» у канала, чтобы начать автоматический импорт гайдов.'
                  : 'Попробуйте изменить поисковый запрос.'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-white/10 rounded-2xl border border-white/10 overflow-hidden bg-background/50 backdrop-blur-md">
              {filteredSyncedGuides.map((item) => (
                <div
                  key={item.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-4 text-xs hover:bg-white/5 transition-colors"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        Синхронизировано
                      </span>
                      <span className="font-mono text-[11px] text-muted-foreground">
                        ID сообщения: {item.discord_message_id}
                      </span>
                    </div>
                    <div className="font-bold text-foreground text-sm line-clamp-1">
                      {item.title}
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-muted-foreground flex-wrap">
                      <span>
                        Автор: <strong className="text-foreground">{item.author_tag}</strong>
                      </span>
                      <span>
                        • Категория: <strong className="text-primary">{item.category_key}</strong>
                      </span>
                      {item.created_at && (
                        <span>
                          • <Clock className="inline size-3 mr-1" />
                          {new Date(item.created_at).toLocaleString('ru-RU')}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <a
                      href={`#/guide/${item.guide_key}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-black uppercase tracking-wider bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:from-violet-500 hover:to-indigo-500 transition-all border border-white/10 shadow-md"
                    >
                      <ExternalLink className="size-3.5" /> Открыть
                    </a>

                    <Button
                      variant="outline"
                      size="sm"
                      disabled={deletingSyncedId === item.id}
                      className="h-9 px-3 text-xs font-bold text-rose-400 border-rose-500/30 hover:bg-rose-500/20 rounded-xl cursor-pointer"
                      onClick={() => handleDeleteSyncedGuide(item.id, false)}
                      title="Удалить эту запись из очереди (гайд на сайте сохранится)"
                    >
                      <Trash2 className="size-3.5" />
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      disabled={deletingSyncedId === item.id}
                      className="h-9 px-3 text-xs font-bold text-rose-400 bg-rose-500/10 border-rose-500/40 hover:bg-rose-500/30 rounded-xl cursor-pointer"
                      onClick={() => handleDeleteSyncedGuide(item.id, true)}
                      title="Удалить эту запись из очереди И удалить гайд с сайта"
                    >
                      <Trash2 className="size-3.5" /> + Гайд
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 items-start">
        <Card className="xl:col-span-5 p-8 border-none bg-card/40 backdrop-blur-sm space-y-6 shadow-2xl ring-1 ring-white/5">
          <div className="flex items-center justify-between">
            <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-foreground/40">
              Ввод: JSON из Discord
            </h3>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-3 text-[9px] uppercase font-bold hover:bg-destructive/10 hover:text-destructive"
              onClick={() => setJsonInput('')}
            >
              Очистить
            </Button>
          </div>
          <Textarea
            className="min-h-[550px] font-mono text-[11px] bg-muted/20 border-none focus-visible:ring-primary/20 p-6 rounded-2xl no-scrollbar"
            placeholder='[{"content": "Hello :fire:", "author": {"username": "HalfSquirrel"}}, ...]'
            value={jsonInput}
            onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setJsonInput(e.target.value)}
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
                  <div className="text-[10px] font-black text-primary uppercase tracking-widest opacity-60">
                    Целевой гайд
                  </div>
                  <select
                    className="w-full h-11 bg-background/50 border-none rounded-xl px-3 text-xs font-bold focus:ring-2 focus:ring-primary/20 appearance-none cursor-pointer"
                    value={selectedGuideKey}
                    onChange={(e) => setSelectedGuideKey(e.target.value)}
                  >
                    <option value="new">+ Создать новый гайд</option>
                    <optgroup label="Существующие гайды (Заменить)">
                      {allGuides.map((g) => (
                        <option key={g.key} value={g.key}>
                          {g.title}
                        </option>
                      ))}
                    </optgroup>
                  </select>
                </div>

                {selectedGuideKey === 'new' && categories.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-[10px] font-black text-primary uppercase tracking-widest opacity-60">
                      Категория
                    </div>
                    <select
                      className="w-full h-11 bg-background/50 border-none rounded-xl px-3 text-xs font-bold focus:ring-2 focus:ring-primary/20 appearance-none cursor-pointer"
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                    >
                      {categories.map((c) => (
                        <option key={c.key} value={c.key}>
                          {c.title}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                <div className="space-y-2">
                  <div className="text-[10px] font-black text-primary uppercase tracking-widest opacity-60">
                    Название гайда
                  </div>
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
                      {selectedGuideKey === 'new'
                        ? 'Будет создан новый объект в базе'
                        : `Обновит контент гайда: ${selectedGuideKey}`}
                    </span>
                  </div>
                  <div className="px-3 py-1 bg-primary text-primary-foreground rounded-lg text-[9px] font-black uppercase tracking-widest">
                    {result.status}
                  </div>
                </div>
              </div>

              <div className="flex-1 p-8 bg-muted/20 rounded-[32px] border border-white/5 space-y-4 shadow-inner relative overflow-hidden">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-[10px] font-black text-muted-foreground/40 uppercase tracking-widest">
                    Содержимое гайда
                  </div>
                  <div className="px-3 py-1 bg-muted/40 rounded-full text-[9px] font-bold text-primary/60 border border-primary/5">
                    {result.media_count} медиа-файлов
                  </div>
                </div>
                <div className="max-h-[400px] overflow-y-auto no-scrollbar pr-2">
                  <FormattedContent text={result.content} />
                </div>
              </div>

              {result.media_files && result.media_files.length > 0 && (
                <div className="space-y-2">
                  <div className="text-[10px] font-black text-muted-foreground/40 uppercase">
                    Найденные медиа (Временные ссылки)
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {result.media_files.slice(0, 3).map((f, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-2 bg-muted/10 rounded-xl text-[10px] font-mono truncate"
                      >
                        <span className="truncate flex-1 pr-2">{f.filename}</span>
                        <span className="text-primary/40 shrink-0">{f.content_type}</span>
                      </div>
                    ))}
                    {result.media_files.length > 3 && (
                      <div className="text-[9px] text-center text-muted-foreground italic">
                        и еще {result.media_files.length - 3} файла...
                      </div>
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
                      <span>
                        {importProgress.current}/{importProgress.total}
                      </span>
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
                    {isTranslating ? (
                      <RefreshCcw className="size-3.5 animate-spin" />
                    ) : (
                      <Globe className="size-3.5" />
                    )}
                    Перевести (AI)
                  </Button>
                  <Button
                    variant="secondary"
                    className="flex-1 rounded-2xl text-xs gap-2"
                    onClick={() => {
                      navigator.clipboard.writeText(result.content)
                      alert('Текст скопирован!')
                    }}
                  >
                    <Copy className="size-3.5" />
                    Копировать текст
                  </Button>
                </div>
              </div>

              {isImporting && (
                <div className="p-4 bg-primary/10 rounded-2xl border border-primary/20 animate-in slide-in-from-bottom-2">
                  <div className="text-[10px] font-black text-primary uppercase tracking-[0.2em] mb-1">
                    Процесс автоматизации
                  </div>
                  <div className="text-xs font-bold text-foreground/80">
                    {importProgress.status}
                  </div>
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
    // Ищем {{icon:name}}, <a:name:id>, <:name:id>, :name:, ![type](url), и прямые ссылки Discord
    return text.split(
      /(\{\{icon:[^}]+\}\}|<a?:[a-zA-Z0-9_]+:\d+>|:[a-zA-Z0-9_]+:|!\[(?:image|video)\]\(.*?\)|https?:\/\/(?:cdn|media)\.discordapp\.(?:com|net)\/attachments\/\d+\/\d+\/[\w.-]+(?:\?[\w=&.%-]+)?)/g
    )
  }, [text])

  return (
    <div className="text-sm leading-relaxed whitespace-pre-wrap opacity-90">
      {parts.map((part, i) => {
        // 0. Обработка нового формата {{icon:name}}
        const iconTokenMatch =
          part.match(/^\{\{icon:([^}]+)\}\}$ /) || part.match(/^\{\{icon:([^}]+)\}\}$ /)
        // Correcting regex for token
        if (part.startsWith('{{icon:') && part.endsWith('}}')) {
          const name = part.slice(7, -2)
          const url = getGameIconUrl(name)
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

        // 1. Обработка Discord эмодзи
        const emojiMatch =
          part.match(/<(a?):([a-zA-Z0-9_]+):(\d+)>/) || part.match(/^:([a-zA-Z0-9_]+):$/)
        if (emojiMatch) {
          let name = ''
          let url = null

          if (emojiMatch.length === 4) {
            const isAnimated = emojiMatch[1] === 'a'
            name = emojiMatch[2]
            const id = emojiMatch[3]
            url = getGameIconUrl(name)
            if (!url) {
              url = apiGetProxyUrl(
                `https://cdn.discordapp.com/emojis/${id}.${isAnimated ? 'gif' : 'webp'}?size=48`
              )
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
        if (
          part.startsWith('http') &&
          (part.includes('discordapp.com') || part.includes('discordapp.net'))
        ) {
          const proxiedUrl = apiGetProxyUrl(part)
          const isVideo =
            part.toLowerCase().split('?')[0].endsWith('.mp4') ||
            part.toLowerCase().split('?')[0].endsWith('.mov')

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
