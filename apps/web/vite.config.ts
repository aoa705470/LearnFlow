import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

const repositoryRoot = fileURLToPath(new URL('../..', import.meta.url))

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, repositoryRoot, '')
  const proxyTarget = env.VITE_API_PROXY_TARGET

  if (command === 'serve' && !proxyTarget) {
    throw new Error(
      'VITE_API_PROXY_TARGET is required when starting the development server.',
    )
  }

  return {
    envDir: repositoryRoot,
    plugins: [vue(), tailwindcss()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      proxy: proxyTarget
        ? {
            '/api': {
              target: proxyTarget,
              changeOrigin: false,
            },
          }
        : undefined,
    },
  }
})
