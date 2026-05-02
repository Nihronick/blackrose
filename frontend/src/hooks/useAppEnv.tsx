import { useState, useEffect, createContext, useContext, useCallback, ReactNode, FC } from 'react';
import { useAppStore } from '../store';

export type AppEnvironment = {
  isTMA: boolean;
  isInTelegram: boolean;
  platform: string;
  version: string;
  tg?: any;
  colorScheme: 'light' | 'dark';
};

const AppEnvContext = createContext<AppEnvironment | null>(null);

export const detectEnvironment = (): AppEnvironment => {
  if (typeof window === 'undefined') {
    return { isTMA: false, isInTelegram: false, platform: 'web', version: '0.0', colorScheme: 'light' };
  }

  const tg = (window as any).Telegram?.WebApp;
  const isTMA = Boolean(tg?.initDataUnsafe?.user);
  const isInTelegram = tg?.version !== undefined;
  
  return {
    isTMA,
    isInTelegram,
    tg,
    platform: tg?.platform || 'web',
    version: tg?.version || '0.0',
    colorScheme: tg?.colorScheme || 'light'
  };
};

interface AppEnvProviderProps {
  children: ReactNode;
}

export const AppEnvProvider: FC<AppEnvProviderProps> = ({ children }) => {
  const [env, setEnv] = useState<AppEnvironment>(detectEnvironment());
  const { setIsTMA, setEnvData } = useAppStore();

  const syncToStore = useCallback((data: AppEnvironment) => {
    setIsTMA(data.isTMA);
    setEnvData({
      platform: data.platform,
      version: data.version,
      colorScheme: data.colorScheme
    });
  }, [setIsTMA, setEnvData]);

  useEffect(() => {
    const currentEnv = detectEnvironment();
    setEnv(currentEnv);
    syncToStore(currentEnv);
    
    if (currentEnv.isTMA && currentEnv.tg) {
      const { tg } = currentEnv;
      
      try {
        tg.ready();
        tg.expand();
        
        const handleUpdate = () => {
          const fresh = detectEnvironment();
          setEnv(fresh);
          syncToStore(fresh);
        };

        tg.onEvent('viewportChanged', handleUpdate);
        tg.onEvent('themeChanged', handleUpdate);
        
        return () => {
          tg.offEvent('viewportChanged', handleUpdate);
          tg.offEvent('themeChanged', handleUpdate);
        };
      } catch (e) {
        console.warn('TMA Init failed:', e);
      }
    }
    
    const root = document.documentElement;
    root.classList.add(currentEnv.isTMA ? 'env-tma' : 'env-web');
    if (currentEnv.platform === 'ios') root.classList.add('platform-ios');
    
    return () => {
      root.classList.remove('env-tma', 'env-web', 'platform-ios');
    };
  }, [syncToStore]);

  return <AppEnvContext.Provider value={env}>{children}</AppEnvContext.Provider>;
}

export const useAppEnv = () => {
  const context = useContext(AppEnvContext);
  if (!context) return detectEnvironment();
  return context;
};
