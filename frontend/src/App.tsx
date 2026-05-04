import { AppLayout } from '@/app/AppLayout'
import { AppProvider } from '@/app/AppProvider'
import { AppRouter } from '@/app/AppRouter'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import type { FC } from 'react'

export const App: FC = () => {
  return (
    <ErrorBoundary>
      <AppProvider>
        <AppLayout>
          <AppRouter />
        </AppLayout>
      </AppProvider>
    </ErrorBoundary>
  )
}

export default App
