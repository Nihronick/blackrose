import { cn } from '@/lib/utils'
import type { ComponentPropsWithoutRef } from 'react'
import { forwardRef } from 'react'

const Label = forwardRef<HTMLLabelElement, ComponentPropsWithoutRef<'label'>>(
  ({ className, ...props }, ref) => (
    <label
      ref={ref}
      className={cn(
        'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
        className
      )}
      {...props}
    />
  )
)
Label.displayName = 'Label'

export { Label }
