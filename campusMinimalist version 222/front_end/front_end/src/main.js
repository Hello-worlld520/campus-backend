import { createApp } from 'vue' // 导入Vue 3的应用创建函数
import { createPinia } from 'pinia' // 导入Pinia（Vue 3官方状态管理）
import App from './App.vue' // 导入根组件
import router from './router' // 导入Vue Router路由实例
import store from './store' // 导入Vuex（兼容旧版状态管理）

// 引入 Element Plus 组件库及样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 导入 Element Plus 所有图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 1. 创建Vue应用实例
const app = createApp(App)
// 2. 创建Pinia实例
const pinia = createPinia()

// 3. 全局注册 Element Plus 所有图标（可直接在模板中使用，无需单独导入）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 4. 安装插件/状态管理
app.use(pinia) // 挂载Pinia
app.use(store) // 挂载Vuex（注意：Vue 3中Pinia和Vuex建议二选一，避免冲突）
app.use(router) // 挂载路由
// 挂载Element Plus，并全局配置默认尺寸为'default'（可选：'large'/'small'）
app.use(ElementPlus, { size: 'default' })

// 5. 将应用挂载到index.html中id为'app'的DOM节点上
app.mount('#app')