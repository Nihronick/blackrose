import { FC } from 'react'
import { AppProvider } from '@/app/AppProvider'
import { AppLayout } from '@/app/AppLayout'
import { AppRouter } from '@/app/AppRouter'
import { ErrorBoundary } from '@/components/ErrorBoundary'

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
