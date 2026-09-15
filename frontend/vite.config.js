import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 前后端分离：前端统一使用相对路径 /api 调用，由 Vite 代理到本地后端服务
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    },
    // Node 26 在 Windows 下的原生文件监听遇到编辑器/工具产生的临时文件会抛 EBUSY 导致 dev server 退出，
    // 改用轮询监听规避（原型规模小，开销可忽略）。详见 README「运行环境说明」。
    watch: {
      usePolling: true,
      interval: 400,
      ignored: ['**/node_modules/**', '**/.git/**', '**/*.tmpdir/**']
    }
  },
  // 渲染级自测（阶段9 验收用）：node 环境下挂载页面组件，验证真实渲染结果
  test: {
    environment: 'happy-dom',
    globals: true,
    include: ['tests/**/*.spec.js']
  }
})
