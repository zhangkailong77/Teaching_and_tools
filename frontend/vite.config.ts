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
    ],
    // API代理配置
    proxy: {
      '/api': {
        target: 'http://192.168.150.27:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
        // 添加代理日志，方便调试
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('[Vite Proxy]', req.method, req.url, '->', proxyReq.path);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('[Vite Proxy]', proxyRes.statusCode, req.url);
          });
        }
      },
      // ComfyUI 代理 - 开发环境使用
      // 格式: /comfyui/username/port/* -> http://192.168.150.2:port/*
      '/comfyui': {
        target: 'http://192.168.150.2',
        changeOrigin: true,
        secure: false,
        ws: true,
        // 这里的 rewrite 只是移除 /comfyui/username/ 前缀，端口通过 configure 动态设置
        rewrite: (path) => path.replace(/^\/comfyui\/[^/]+\/\d+/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            const originalPath = req.url || '';
            // 提取端口: /comfyui/username/8189/api/xxx -> 8189
            const portMatch = originalPath.match(/\/comfyui\/[^/]+\/(\d+)/);
            if (portMatch) {
              const port = portMatch[1];
              // 修改请求路径，去掉 /comfyui/username/
              const newPath = '/' + originalPath.split('/').slice(4).join('/');
              proxyReq.path = newPath;
              // 注意：Vite/http-proxy 不支持动态修改 target
              // 开发环境需要直接访问 GPU 服务器，或使用其他方案
              console.log('[ComfyUI Proxy]', req.method, 'port:', port, 'path:', newPath);
            }
          });
        }
      },
      // 静态资源代理
      '/static/js/comfyui-queue.js': {
        target: 'http://192.168.150.27:5173',
        changeOrigin: true
      }
    }
  }
})
