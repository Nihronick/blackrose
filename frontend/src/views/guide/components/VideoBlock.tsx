import { Play } from '@/lib/icons'
import { normalizeUrl, parseVideo } from '@/lib/utils'

export const VideoBlock: React.FC<{ url: string }> = ({ url }) => {
  const v = parseVideo(normalizeUrl(url))
  if (!v) return null

  const normalizedUrl = normalizeUrl(url)

  if (v.type === 'youtube')
    return (
      <div className="relative my-4 aspect-video overflow-hidden rounded-2xl shadow-xl border border-border/50">
        <iframe
          className="absolute inset-0 size-full"
          src={`https://www.youtube.com/embed/${v.id}`}
          allowFullScreen
          title="video"
        />
      </div>
    )

  if (v.type === 'video')
    return (
      <div className="relative my-4 overflow-hidden rounded-2xl shadow-xl border border-border/50 bg-black group">
        <video controls preload="none" playsInline className="w-full aspect-video">
          <source src={normalizedUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
    )

  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="my-3 flex items-center gap-3 rounded-xl bg-muted/30 p-4 font-semibold text-primary transition-colors hover:bg-muted active:scale-[0.98]"
    >
      <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <Play className="size-5 fill-current" />
      </div>
      Смотреть видео
    </a>
  )
}
