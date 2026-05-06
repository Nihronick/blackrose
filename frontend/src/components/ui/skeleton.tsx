import { cn } from '@/lib/utils'
import type { ComponentProps } from 'react'

function Skeleton({ className, ...props }: ComponentProps<'div'>) {
  return (
    <div
      data-slot="skeleton"
      className={cn('skeleton rounded-md bg-muted/40', className)}
      {...props}
    />
  )
}

export { Skeleton }
