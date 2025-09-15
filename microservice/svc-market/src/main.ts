import { createApp } from 'vue'
import App from './App.vue'

// AG Grid 样式导入
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

// AG Grid 模块注册
import { ModuleRegistry } from 'ag-grid-community'
import { ClientSideRowModelModule } from 'ag-grid-community'

// 注册 AG Grid 社区版模块
ModuleRegistry.registerModules([ClientSideRowModelModule])

// 全局样式
import './styles/global.css'

const app = createApp(App)

app.mount('#app')