import { Skeleton } from '@/components/ui/skeleton'
import type { FC } from 'react'
import type React from 'react'

export const SkeletonCard: FC = () => {
  return (
    <div className="flex items-center gap-4 rounded-2xl border border-border/50 bg-card p-4">
      <Skeleton className="size-14 rounded-2xl shrink-0" />
      <div className="flex flex-1 flex-col gap-2">
        <Skeleton className="h-5 w-[60%] rounded-md" />
        <Skeleton className="h-3 w-[40%] rounded-md" />
      </div>
      <Skeleton className="size-5 rounded-full shrink-0" />
    </div>
  )
}

export const SkeletonList: FC<{ count?: number }> = ({ count = 6 }) => {
  return (
    <div className="grid grid-cols-1 gap-4 px-5 py-6">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  )
}

export const SkeletonGuide: FC = () => {
  return (
    <div className="flex flex-col gap-6 px-6 py-8">
      <div className="flex flex-col items-center gap-4">
        <Skeleton className="size-20 rounded-[28px]" />
        <Skeleton className="h-8 w-[70%] rounded-lg" />
      </div>
      <div className="flex flex-col gap-3 mt-4">
        {[95, 88, 72, 95, 60, 82, 50, 78].map((w, i) => (
          <Skeleton key={i} className="h-4 rounded-md" style={{ width: `${w}%` }} />
        ))}
      </div>
    </div>
  )
}
