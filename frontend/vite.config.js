import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    hmr: {
      overlay: false,  // Disable error overlay that can cause issues
      protocol: 'ws',  // Use WebSocket protocol
      host: 'localhost',
      port: 24678  // Default HMR port
    },
    watch: {
      usePolling: true  // More reliable file watching
    },
    force: true  // Force dependency pre-bundling
  },
  optimizeDeps: {
    force: true  // Force dependency optimization
  },
  build: {
    manifest: true,  // Generate manifest for better caching
    modulePreload: {
      polyfill: true  // Add module preload polyfill
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'pinia', 'vue-router'],  // Separate vendor chunks
          'ui': ['@aksharahegde/vue-glow']  // UI library chunk
        }
      }
    },
    chunkSizeWarningLimit: 1000  // Increase chunk size warning limit
  }
})
