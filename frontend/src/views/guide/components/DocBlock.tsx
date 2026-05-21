import { Download, FileText } from '@/lib/icons'
import { normalizeUrl, parseDocument } from '@/lib/utils'
import type { FC } from 'react'

export const DocBlock: FC<{ url: string }> = ({ url }) => {
  const normalizedUrl = normalizeUrl(url)
  const d = parseDocument(normalizedUrl)
  if (!d) return null

  return (
    <a
      href={d.url}
      target="_blank"
      rel="noreferrer"
      className="group my-3 flex items-center gap-4 rounded-xl border border-border/50 bg-card p-4 transition-all hover:bg-accent hover:shadow-md active:scale-[0.98]"
    >
      <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-muted transition-colors group-hover:bg-background">
        <FileText className="size-6 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate text-sm font-bold text-foreground">{d.name}</div>
        <div className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60 flex items-center gap-1.5 mt-1">
          <layui-badge
            color="cyan"
            class="text-[9px] font-semibold py-0.5 px-1.5 uppercase rounded-md"
          >
            {d.ext}
          </layui-badge>{' '}
          Document
        </div>
      </div>
      <Download className="size-5 text-muted-foreground/30 transition-transform group-hover:translate-x-0 group-hover:text-primary" />
    </a>
  )
}
