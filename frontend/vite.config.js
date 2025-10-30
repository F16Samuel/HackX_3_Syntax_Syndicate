import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path' // <-- ADD THIS LINE

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { // <-- ADD THIS ENTIRE BLOCK
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
