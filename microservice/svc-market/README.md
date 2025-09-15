# DAOTrader 行情服务中台

基于 AG Grid 的专业金融数据表格服务，提供实时行情数据展示和管理功能。

## 🚀 快速开始

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:3001 查看应用

### 构建生产版本
```bash
npm run build
```

## 📋 功能特性

### ✅ 已实现功能
- 🏗️ **基础架构**: Vue 3 + TypeScript + Vite
- 📊 **AG Grid 集成**: 专业金融数据表格
- 🎨 **响应式UI**: 现代化界面设计
- 📈 **实时数据**: 模拟行情数据更新
- 🔄 **数据刷新**: 手动和自动刷新功能
- 📱 **多市场支持**: 国内期货、国际期货、A股、H股、美股、外汇、数字币
- 🎯 **视图切换**: 表格视图和图表视图

### 🚧 开发中功能
- 📈 **图表视图**: K线图、技术指标图表
- 🔌 **WebSocket**: 实时数据推送
- 💾 **数据持久化**: 历史数据存储
- 🔍 **高级筛选**: 多条件数据筛选
- 📊 **自定义指标**: 技术分析指标
- 🎛️ **个性化配置**: 用户偏好设置

## 🏗️ 技术架构

### 核心技术栈
- **前端框架**: Vue 3.3+ (Composition API)
- **开发语言**: TypeScript 5.2+
- **构建工具**: Vite 4.5+
- **数据表格**: AG Grid Community 31.0+
- **样式方案**: 原生CSS + CSS变量

### 项目结构
```
src/
├── App.vue              # 主应用组件
├── main.ts              # 应用入口
└── styles/
    └── global.css       # 全局样式
```

## 📊 AG Grid 配置

### 列定义 (Column Definitions)
- **代码**: 合约/股票代码
- **名称**: 中文名称
- **最新价**: 实时价格 (带涨跌颜色)
- **涨跌**: 价格变动
- **涨跌幅**: 百分比变动
- **成交量**: 格式化显示 (万/亿)
- **开盘价**: 当日开盘价
- **最高价**: 当日最高价
- **最低价**: 当日最低价
- **昨收价**: 前一交易日收盘价

### 表格特性
- ✅ 列排序和筛选
- ✅ 列宽调整
- ✅ 行选择
- ✅ 右键菜单
- ✅ 数据导出
- ✅ 实时数据更新
- ✅ 金融数据格式化
- ✅ 涨跌颜色标识

## 🎨 样式主题

### 金融主题 (Financial Theme)
基于 AG Grid Alpine 主题定制的金融数据专用主题:

- **字体**: SF Pro Text / SF Mono (等宽数字)
- **配色**: 专业金融配色方案
- **涨跌色**: 红涨绿跌 (中国习惯)
- **响应式**: 支持移动端适配

### CSS 变量
```css
--ag-font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont;
--ag-font-size: 12px;
--ag-foreground-color: #2d3748;
--ag-background-color: #ffffff;
--ag-header-background-color: #f7fafc;
--ag-row-height: 32px;
--ag-header-height: 36px;
```

## 🔄 数据模拟

### 模拟数据结构
```typescript
interface MarketData {
  symbol: string;        // 代码
  name: string;          // 名称
  price: number;         // 最新价
  change: number;        // 涨跌
  changePercent: number; // 涨跌幅
  volume: number;        // 成交量
  open: number;          // 开盘价
  high: number;          // 最高价
  low: number;           // 最低价
  prevClose: number;     // 昨收价
}
```

### 实时更新
- 每2秒随机更新一行数据
- 模拟真实市场波动
- 支持手动刷新全部数据

## 🚀 部署说明

### 开发环境
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问地址
http://localhost:3001
```

### 生产环境
```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

### Docker 部署 (可选)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "run", "preview"]
```

## 🔧 配置说明

### Vite 配置
- 端口: 3001
- 代理: 支持后端API代理
- 构建优化: AG Grid 依赖分包
- 开发工具: Vue DevTools 支持

### TypeScript 配置
- 严格模式: 启用
- 路径映射: `@/*` -> `src/*`
- 类型检查: 完整支持

## 📈 性能优化

### AG Grid 优化
- 虚拟滚动: 大数据集支持
- 增量更新: 只更新变化的行
- 列虚拟化: 大量列支持
- 内存管理: 自动垃圾回收

### 构建优化
- 代码分割: 按需加载
- 依赖分包: AG Grid 单独打包
- 压缩优化: Gzip/Brotli 支持
- 缓存策略: 长期缓存

## 🐛 常见问题

### Q: AG Grid 模块导入错误
A: 确保使用正确的模块导入方式:
```typescript
import { ModuleRegistry, ClientSideRowModelModule } from 'ag-grid-community';
ModuleRegistry.registerModules([ClientSideRowModelModule]);
```

### Q: 样式不生效
A: 确保正确导入 AG Grid 样式:
```typescript
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
```

### Q: 数据不更新
A: 检查 `getRowId` 配置和数据结构:
```typescript
gridOptions: {
  getRowId: (params) => params.data.symbol
}
```

## 📚 参考文档

- [AG Grid Vue 文档](https://www.ag-grid.com/vue-data-grid/)
- [Vue 3 官方文档](https://vuejs.org/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Vite 文档](https://vitejs.dev/)

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**DAOTrader Team** - 专业的量化交易平台