import type React from 'react'
import { Suspense } from 'react'
import { ErrorBoundary } from './ErrorBoundary'
import { SkeletonList } from './Skeletons'

interface FeatureBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export const FeatureBoundary: React.FC<FeatureBoundaryProps> = ({
  children,
  fallback = <SkeletonList count={7} />,
}) => {
  return (
    <ErrorBoundary>
      <Suspense fallback={fallback}>{children}</Suspense>
    </ErrorBoundary>
  )
}
