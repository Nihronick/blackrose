import { ComponentProps } from 'react';
import { cn } from '@/lib/utils'

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
