import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.blackrose.slayerlegend',
  appName: 'BlackRose',
  webDir: 'dist',
  server: {
    // В production убрать url — будет использовать локальный dist
    // url: 'https://blackrose-9es.pages.dev',
    androidScheme: 'https',
    iosScheme: 'https',
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#1c1c1e',
    },
    SplashScreen: {
      launchShowDuration: 1500,
      backgroundColor: '#1c1c1e',
      androidSplashResourceName: 'splash',
      showSpinner: false,
      launchAutoHide: true,
    },
  },
  android: {
    backgroundColor: '#1c1c1e',
    allowMixedContent: true,
  },
  ios: {
    backgroundColor: '#1c1c1e',
    contentInset: 'automatic',
    preferredContentMode: 'mobile',
    scheme: 'BlackRose',
  },
}

export default config
