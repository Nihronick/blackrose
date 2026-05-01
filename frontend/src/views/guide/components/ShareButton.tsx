import { Button } from '@/components/ui/button'
import { haptic } from '@/lib/haptic'
import { Check, Share2 } from '@/lib/icons'
import type React from 'react'
import { useState } from 'react'

interface Telegram {
  WebApp: {
    openTelegramLink: (url: string) => void
  }
}

interface ShareButtonProps {
  guide: {
    key: string
    title: string
  }
}

export const ShareButton: React.FC<ShareButtonProps> = ({ guide }) => {
  const [shared, setShared] = useState(false)

  const share = () => {
    haptic.light()
    const botUsername = 'blackrosesl1_bot'
    const deepLink = `https://t.me/${botUsername}?start=guide_${guide.key}`

    const markShared = () => {
      setShared(true)
      haptic.success?.()
      setTimeout(() => setShared(false), 2000)
    }

    const tgApp = (window as unknown as { Telegram?: Telegram })?.Telegram?.WebApp
    if (tgApp?.openTelegramLink) {
      tgApp.openTelegramLink(
        `https://t.me/share/url?url=${encodeURIComponent(deepLink)}&text=${encodeURIComponent(guide.title)}`
      )
      markShared()
      return
    }

    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(deepLink).then(markShared)
      return
    }

    _fallbackCopy(deepLink, markShared)
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={share}
      className="size-10 rounded-full transition-transform active:scale-95"
    >
      {shared ? (
        <Check className="size-5 text-green-500" />
      ) : (
        <Share2 className="size-5 text-muted-foreground" />
      )}
    </Button>
  )
}

function _fallbackCopy(text: string, onSuccess?: () => void) {
  try {
    const el = document.createElement('textarea')
    el.value = text
    el.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0'
    document.body.appendChild(el)
    el.focus()
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
    onSuccess?.()
  } catch {}
}
