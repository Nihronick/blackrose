import { Card } from '@/components/ui/card'
import { apiMediaList } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { Copy, Film, Image as ImageIcon, Search } from '@/lib/icons'
import { normalizeUrl } from '@/lib/utils'
import type React from 'react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'

export const MediaTab: React.FC = () => {
  const [data, setData] = useState<{ groups: any[]; total: number } | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    apiMediaList()
      .then(setData)
      .finally(() => setLoading(false))
  }, [])

  if (loading)
    return (
      <div className="flex h-60 items-center justify-center">
        <div className="adm2-spinner" />
      </div>
    )

  const filteredGroups = data?.groups.map(group => ({
    ...group,
    items: group.items.filter((item: any) => 
      item.name.toLowerCase().includes(search.toLowerCase())
    )
  })).filter(group => group.items.length > 0) || []

  const copyToClipboard = (url: string) => {
    navigator.clipboard.writeText(url)
    haptic.success()
    toast.success('Ссылка скопирована')
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-black tracking-tight uppercase">Библиотека медиа ({data?.total})</h2>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground/40" />
          <input
            className="w-full bg-muted/40 border-none rounded-xl h-10 pl-10 pr-4 text-sm font-medium focus:ring-1 ring-primary/20 transition-all outline-none"
            placeholder="Поиск по названию..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="flex flex-col gap-10">
        {filteredGroups.map((group) => (
          <section key={group.id} className="space-y-4">
            <div className="flex items-center gap-2 px-2">
              <div className="h-4 w-1 bg-primary rounded-full" />
              <h3 className="text-sm font-black uppercase tracking-widest text-foreground/60">
                {group.label}
              </h3>
              <span className="text-[10px] font-bold text-muted-foreground/30 px-2 py-0.5 bg-muted/20 rounded-full">
                {group.items.length}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
              {group.items.map((item: any, i: number) => (
                <Card 
                  key={i} 
                  className="group relative aspect-square overflow-hidden border-none bg-muted/20 hover:ring-2 ring-primary/40 transition-all cursor-pointer"
                  onClick={() => copyToClipboard(item.url)}
                >
                  {item.type === 'image' ? (
                    <img 
                      src={normalizeUrl(item.url)} 
                      alt="" 
                      className="size-full object-cover transition-transform duration-500 group-hover:scale-110"
                      loading="lazy"
                    />
                  ) : (
                    <div className="size-full flex flex-col items-center justify-center gap-2 bg-slate-900/40">
                      <Film className="size-8 text-white/40" />
                      <span className="text-[8px] font-black uppercase text-white/60 tracking-widest">Video</span>
                    </div>
                  )}
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-3 gap-2 backdrop-blur-[2px]">
                    <div className="size-8 rounded-full bg-white/20 flex items-center justify-center">
                      <Copy className="size-4 text-white" />
                    </div>
                    <span className="text-[9px] font-bold text-white text-center break-all line-clamp-2 leading-tight">
                      {item.name}
                    </span>
                  </div>

                  <div className="absolute top-2 left-2">
                    {item.type === 'image' ? (
                      <ImageIcon className="size-3 text-white/40" />
                    ) : (
                      <Film className="size-3 text-white/40" />
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </section>
        ))}
      </div>

      {filteredGroups.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground/30">
          <ImageIcon className="size-16 mb-4 opacity-10" />
          <p className="text-sm font-bold uppercase tracking-widest italic">Файлы не найдены</p>
        </div>
      )}
    </div>
  )
}
