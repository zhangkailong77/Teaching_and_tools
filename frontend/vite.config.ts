import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    // 配置路径别名
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',  // 允许局域网访问
    port: 5173,
    strictPort: true,
    allowedHosts: [
      'ai.yz-cube.com',
      // 'all' // 如果不想限制，也可以填 'all' 或者 true，但推荐写具体域名更安全
    ] 
  }
})
