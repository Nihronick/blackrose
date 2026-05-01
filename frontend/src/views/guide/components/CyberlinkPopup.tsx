import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { apiFetch } from '@/lib/api'
import type { Guide } from '@/lib/types'
import { haptic } from '@/lib/haptic'
import { ExternalLink } from '@/lib/icons'
import { formatGuideText } from '@/lib/markdown'
import { useSuspenseQuery } from '@tanstack/react-query'
import type React from 'react'
import { useMemo } from 'react'

interface CyberlinkPopupProps {
  guideKey: string
  title: string
  icon?: string
  onOpen: (key: string, title?: string, icon?: string) => void
  onClose: () => void
}

export const CyberlinkPopup: React.FC<CyberlinkPopupProps> = ({
  guideKey,
  title,
  icon,
  onOpen,
  onClose,
}) => {
  const { data: preview } = useSuspenseQuery({
    queryKey: ['guide', 'preview', guideKey],
    queryFn: () => apiFetch<Guide>(`/api/guide/${guideKey}`),
    staleTime: 60000,
  })

  const previewHtml = useMemo(() => {
    if (!preview?.text) return ''
    return formatGuideText(preview.text, {
      guideLinks: (preview.guide_links as Record<string, { title?: string; icon?: string }>) ?? {},
      iconResolver: (name: string) => preview.icons?.[name] || '',
    })
  }, [preview])

  return (
    <Sheet open onOpenChange={onClose}>
      <SheetContent side="bottom" className="flex flex-col gap-0 rounded-t-[32px] p-0 h-[85vh]">
        <SheetHeader className="px-6 py-4 border-b">
          <div className="flex items-center gap-3">
            <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-muted">
              {icon ? (
                <img src={icon} alt="" className="size-7 object-contain" />
              ) : (
                <span className="text-xl">📄</span>
              )}
            </div>
            <SheetTitle className="truncate text-lg font-bold tracking-tight">{title}</SheetTitle>
          </div>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div
            className="guide-content prose prose-invert max-w-none prose-img:rounded-xl"
            dangerouslySetInnerHTML={{ __html: previewHtml }}
          />
        </div>

        <SheetFooter className="p-6 border-t bg-muted/20">
          <Button
            className="w-full h-14 rounded-2xl text-base font-bold shadow-lg shadow-primary/20"
            onClick={() => {
              haptic.select()
              onOpen(guideKey, preview?.title, preview?.icon)
              onClose()
            }}
          >
            <ExternalLink className="mr-2 size-5" />
            Открыть полный гайд
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
