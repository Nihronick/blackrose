// @ts-nocheck
import { Button } from '@/components/ui/button'
import { AlertCircle, RefreshCw, XCircle } from '@/lib/icons'
import Honeybadger from '@honeybadger-io/js'
import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

/**
 * ErrorBoundary refactored with TSX, shadcn/ui and premium visuals.
 * Handles React runtime crashes with graceful fallback and logging.
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    if (import.meta.env.VITE_HONEYBADGER_API_KEY) {
      Honeybadger.notify(error, { context: { react: info.componentStack } })
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-[80vh] flex-col items-center justify-center px-8 text-center animate-in fade-in duration-500">
          <div className="flex size-20 items-center justify-center rounded-[28px] bg-destructive/10 text-destructive mb-6 ring-1 ring-destructive/20 shadow-lg shadow-destructive/5">
            <AlertCircle className="size-10" />
          </div>
          <h2 className="text-2xl font-black tracking-tight text-foreground mb-3">
            Что-то пошло не так
          </h2>
          <p className="max-w-[280px] text-sm font-medium text-muted-foreground leading-relaxed">
            Приложение столкнулось с неожиданной ошибкой. Попробуйте обновить страницу или перезайти
            в бот.
          </p>

          <div className="flex flex-col gap-3 w-full max-w-[240px] mt-8">
            <Button
              className="h-12 rounded-2xl font-bold shadow-lg shadow-primary/20 active:scale-95 transition-all w-full"
              onClick={() => window.location.reload()}
            >
              <RefreshCw className="mr-2 size-4" />
              Обновить
            </Button>

            {window.Telegram?.WebApp?.version && (
              <Button
                variant="outline"
                className="h-12 rounded-2xl font-bold active:scale-95 transition-all w-full border-border/40"
                onClick={() => window.Telegram?.WebApp?.close()}
              >
                <XCircle className="mr-2 size-4" />
                Закрыть бота
              </Button>
            )}
          </div>

          {process.env.NODE_ENV === 'development' && this.state.error && (
            <pre className="mt-8 max-w-full overflow-auto rounded-xl bg-muted p-4 text-left text-[10px] text-muted-foreground leading-tight">
              {this.state.error.stack}
            </pre>
          )}
        </div>
      )
    }
    return this.props.children
  }
}
