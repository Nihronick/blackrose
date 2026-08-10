import path from 'node:path'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig } from 'vitest/config'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  base: '/',
  plugins: [
    react({
      jsxRuntime: 'automatic',
    }),
    visualizer({
      filename: 'dist/stats.html',
      gzipSize: true,
      brotliSize: true,
      open: false,
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~types': path.resolve(__dirname, './src/types'),
      '~components': path.resolve(__dirname, './src/components'),
      '~features': path.resolve(__dirname, './src/features'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  build: {
    outDir: 'dist',
    target: 'es2022',
    sourcemap: false,
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react-dom') || id.includes('react-router-dom') || id.includes('react/')) {
              return 'vendor-react'
            }
            if (id.includes('framer-motion')) {
              return 'vendor-motion'
            }
            if (id.includes('recharts')) {
              return 'vendor-charts'
            }
            if (id.includes('@tanstack')) {
              return 'vendor-tanstack'
            }
            if (id.includes('lucide-react')) {
              return 'vendor-icons'
            }
          }
        },
      },
    },
  },
  define: {
    'import.meta.env.VITE_RELEASE': JSON.stringify(process.env.RAILWAY_GIT_COMMIT_SHA ?? 'dev'),
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
