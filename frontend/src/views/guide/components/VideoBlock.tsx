import {
  Loader2,
  Maximize,
  Pause,
  PictureInPicture2,
  Play,
  Volume2,
  VolumeX,
} from '@/lib/icons'
import { normalizeUrl, parseVideo } from '@/lib/utils'
import { AnimatePresence, motion } from 'framer-motion'
import React, { useEffect, useRef, useState } from 'react'

export const VideoBlock: React.FC<{ url: string; alt?: string }> = ({ url, alt }) => {
  const v = parseVideo(normalizeUrl(url))
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(true)
  const [isLoading, setIsLoading] = useState(true)
  const [progress, setProgress] = useState(0)
  const [showControls, setShowControls] = useState(true)
  const controlsTimeout = useRef<any>()

  if (!v) return null
  const normalizedUrl = normalizeUrl(url)

  if (v.type === 'youtube')
    return (
      <div className="relative my-6 aspect-video overflow-hidden rounded-3xl shadow-2xl border border-border/10 bg-black">
        <iframe
          className="absolute inset-0 size-full"
          src={`https://www.youtube.com/embed/${v.id}`}
          allowFullScreen
          title="video"
        />
      </div>
    )

  const togglePlay = () => {
    if (!videoRef.current) return
    if (isPlaying) {
      videoRef.current.pause()
    } else {
      videoRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const toggleMute = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!videoRef.current) return
    videoRef.current.muted = !isMuted
    setIsMuted(!isMuted)
  }

  const togglePip = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!videoRef.current) return
    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture()
      } else {
        await videoRef.current.requestPictureInPicture()
      }
    } catch (err) {
      console.error('PiP failed', err)
    }
  }

  const toggleFullscreen = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!videoRef.current) return
    if (videoRef.current.requestFullscreen) {
      videoRef.current.requestFullscreen()
    } else if ((videoRef.current as any).webkitEnterFullscreen) {
      // iOS support
      ;(videoRef.current as any).webkitEnterFullscreen()
    }
  }

  const handleTimeUpdate = () => {
    if (!videoRef.current) return
    const p = (videoRef.current.currentTime / videoRef.current.duration) * 100
    setProgress(p)
  }

  const handleInteraction = () => {
    setShowControls(true)
    if (controlsTimeout.current) clearTimeout(controlsTimeout.current)
    if (isPlaying) {
      controlsTimeout.current = setTimeout(() => setShowControls(false), 3000)
    }
  }

  return (
    <div
      className="group relative my-8 overflow-hidden rounded-[2rem] border border-border/10 bg-black shadow-2xl"
      onMouseMove={handleInteraction}
      onTouchStart={handleInteraction}
      onClick={togglePlay}
    >
      {/* Loading Spinner */}
      {isLoading && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <Loader2 className="size-10 animate-spin text-primary" />
        </div>
      )}

      <video
        ref={videoRef}
        playsInline
        loop
        muted={isMuted}
        className="w-full aspect-video cursor-pointer object-cover"
        onWaiting={() => setIsLoading(true)}
        onCanPlay={() => setIsLoading(false)}
        onTimeUpdate={handleTimeUpdate}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      >
        <source src={normalizedUrl} type="video/mp4" />
      </video>

      {/* Custom UI Controls */}
      <AnimatePresence>
        {showControls && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-10 flex flex-col justify-between p-4 bg-gradient-to-t from-black/80 via-transparent to-black/20 pointer-events-none"
          >
            {/* Top Bar */}
            <div className="flex justify-end gap-2 pointer-events-auto">
              <button
                onClick={togglePip}
                className="flex size-10 items-center justify-center rounded-xl bg-white/10 backdrop-blur-md transition-all hover:bg-white/20 active:scale-90"
              >
                <PictureInPicture2 className="size-5 text-white" />
              </button>
            </div>

            {/* Center Play Button */}
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.button
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                whileHover={{ scale: 1.1 }}
                whileActive={{ scale: 0.9 }}
                className="flex size-20 items-center justify-center rounded-full bg-primary/90 text-white shadow-2xl shadow-primary/30 backdrop-blur-sm pointer-events-auto"
              >
                {isPlaying ? (
                  <Pause className="size-8 fill-current" />
                ) : (
                  <Play className="size-8 fill-current translate-x-1" />
                )}
              </motion.button>
            </div>

            {/* Bottom Controls */}
            <div className="space-y-4 pointer-events-auto">
              {/* Caption if provided */}
              {alt && (
                <div className="text-[11px] font-bold text-white/90 text-center drop-shadow-md px-2">
                  {alt}
                </div>
              )}

              {/* Progress Bar */}
              <div className="relative h-1.5 w-full overflow-hidden rounded-full bg-white/20">
                <motion.div
                  className="absolute h-full bg-primary"
                  style={{ width: `${progress}%` }}
                  transition={{ type: 'spring', bounce: 0, duration: 0.1 }}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={toggleMute}
                    className="flex size-10 items-center justify-center rounded-xl bg-white/10 backdrop-blur-md transition-all hover:bg-white/20 active:scale-90"
                  >
                    {isMuted ? (
                      <VolumeX className="size-5 text-white" />
                    ) : (
                      <Volume2 className="size-5 text-white" />
                    )}
                  </button>
                </div>

                <button
                  onClick={toggleFullscreen}
                  className="flex size-10 items-center justify-center rounded-xl bg-white/10 backdrop-blur-md transition-all hover:bg-white/20 active:scale-90"
                >
                  <Maximize className="size-5 text-white" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Info (if any) */}
      {!isPlaying && !isLoading && (
        <div className="absolute top-4 left-4 z-10 px-3 py-1 rounded-full bg-black/60 text-[10px] font-black uppercase tracking-widest text-white backdrop-blur-md border border-white/10">
          Нажмите для просмотра
        </div>
      )}
    </div>
  )
}
