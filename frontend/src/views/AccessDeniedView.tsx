import { Card } from '@/components/ui/card'
import { ShieldAlert } from '@/lib/icons'
import type React from 'react'

interface AccessDeniedViewProps {
  message?: React.ReactNode
}

export const AccessDeniedView: React.FC<AccessDeniedViewProps> = ({ message }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-background animate-in fade-in duration-500 min-h-[60vh]">
      <Card className="w-full max-w-sm p-10 flex flex-col items-center text-center space-y-6 border-none bg-card/40 backdrop-blur-md shadow-2xl rounded-[32px] ring-1 ring-border/5">
        <div className="p-5 bg-destructive/10 rounded-3xl text-destructive shadow-sm shadow-destructive/10 animate-bounce duration-[2000ms]">
          <ShieldAlert className="size-12" />
        </div>

        <div className="space-y-3">
          <h2 className="text-2xl font-black tracking-tight uppercase">Доступ ограничен</h2>
          <div className="text-sm font-medium text-muted-foreground/80 leading-relaxed">
            {message || (
              <>
                Откройте бота <span className="text-primary font-bold">@blackrosesl1_bot</span>,
                нажмите{' '}
                <span className="bg-muted px-1.5 py-0.5 rounded text-primary font-bold">
                  /start
                </span>{' '}
                и используйте кнопку{' '}
                <span className="text-primary font-bold">«📖 Открыть гайды»</span>.
              </>
            )}
          </div>
        </div>

        <div className="w-full h-[1px] bg-border/10" />

        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/40">
          Security Protocol Alpha
        </div>
      </Card>
    </div>
  )
}
