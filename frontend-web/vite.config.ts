import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),

    // Enable HTTPS in dev so Chrome/Safari on phone allows Web Speech API.
    // basicSsl generates a self-signed cert automatically — no system tools needed.
    // Only active during `npm run dev`; excluded from production builds.
    basicSsl(),

    VitePWA({
      registerType: 'autoUpdate',
      // Don't let the service-worker intercept API calls in dev.
      devOptions: { enabled: false },
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Voice Shopping Assistant',
        short_name: 'VoiceShop',
        description: 'A smart voice-controlled shopping list application',
        theme_color: '#6366F1',
        background_color: '#0F172A',
        display: 'standalone',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },
    }),
  ],

  server: {
    // Expose the dev server on all network interfaces (0.0.0.0) so
    // your phone can reach it over the local Wi-Fi network.
    host: '0.0.0.0',
    port: 5173,
    // Route API requests to the local backend automatically.
    // This allows us to use a SINGLE ngrok tunnel for both frontend and backend!
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/items': 'http://127.0.0.1:8000',
      '/products': 'http://127.0.0.1:8000',
      '/categories': 'http://127.0.0.1:8000',
      '/voice': 'http://127.0.0.1:8000',
    }
  },
})
