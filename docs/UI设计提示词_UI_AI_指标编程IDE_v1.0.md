# UI设计提示词 - 专用指标编程IDE (UI AI) v1.0

## 项目概述

你是一个专业的UI/UX设计师，负责设计专用指标编程IDE的用户界面。这个IDE需要为量化交易指标开发者提供直观、高效的编程环境，支持DSL语言编辑、实时编译预览、文件管理等核心功能。

## 设计目标

### 主要设计目标
1. **专业性** - 体现金融科技产品的专业感和可信度
2. **效率性** - 优化开发者工作流程，提高编程效率
3. **直观性** - 降低学习成本，新用户能快速上手
4. **现代感** - 采用现代化设计语言，符合当前审美趋势
5. **可扩展性** - 界面结构支持未来功能扩展

### 用户体验原则
- **一致性** - 保持整体设计风格统一
- **反馈性** - 及时响应用户操作，提供清晰反馈
- **容错性** - 预防用户错误，提供友好的错误处理
- **可访问性** - 支持键盘导航，考虑视觉障碍用户
- **响应式** - 适配不同屏幕尺寸和分辨率

## 整体设计风格

### 1. 设计语言

**现代简约风格**
- 采用扁平化设计，避免过度装饰
- 注重功能性和可用性
- 使用几何形状和清晰的层次结构
- 保持视觉平衡和空间感

**专业商务感**
- 体现金融科技产品的专业性
- 使用深色主题作为主要界面风格
- 突出数据和代码的可读性
- 营造专注的开发环境氛围

### 2. 色彩系统

**主色调 - 深色主题**
```css
/* 主要背景色 */
--bg-primary: #1e1e1e;        /* 主背景 */
--bg-secondary: #252526;      /* 次要背景 */
--bg-tertiary: #2d2d30;       /* 三级背景 */

/* 表面色 */
--surface-primary: #3c3c3c;   /* 主要表面 */
--surface-secondary: #404040; /* 次要表面 */
--surface-hover: #464647;     /* 悬停状态 */

/* 边框色 */
--border-primary: #454545;    /* 主要边框 */
--border-secondary: #3e3e42;  /* 次要边框 */
--border-focus: #007acc;      /* 焦点边框 */
```

**强调色系**
```css
/* 品牌色 */
--accent-primary: #007acc;    /* 主要强调色（蓝色） */
--accent-secondary: #0e639c;  /* 次要强调色 */
--accent-hover: #1177bb;      /* 悬停状态 */

/* 功能色 */
--success: #4caf50;           /* 成功状态（绿色） */
--warning: #ff9800;           /* 警告状态（橙色） */
--error: #f44336;             /* 错误状态（红色） */
--info: #2196f3;              /* 信息状态（蓝色） */
```

**文本色系**
```css
/* 文本颜色 */
--text-primary: #cccccc;      /* 主要文本 */
--text-secondary: #969696;    /* 次要文本 */
--text-disabled: #656565;     /* 禁用文本 */
--text-inverse: #ffffff;      /* 反色文本 */

/* 代码高亮色 */
--code-keyword: #569cd6;      /* 关键字 */
--code-string: #ce9178;       /* 字符串 */
--code-number: #b5cea8;       /* 数字 */
--code-comment: #6a9955;      /* 注释 */
--code-function: #dcdcaa;     /* 函数名 */
--code-variable: #9cdcfe;     /* 变量名 */
```

### 3. 字体系统

**代码字体**
```css
/* 等宽字体 - 用于代码编辑器 */
font-family: 'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace;
font-size: 14px;
line-height: 1.5;
font-weight: 400;

/* 支持连字符（ligatures） */
font-variant-ligatures: common-ligatures;
```

**界面字体**
```css
/* 无衬线字体 - 用于界面文本 */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;

/* 字体大小层级 */
--font-size-xs: 12px;         /* 辅助信息 */
--font-size-sm: 13px;         /* 次要文本 */
--font-size-base: 14px;       /* 基础文本 */
--font-size-lg: 16px;         /* 重要文本 */
--font-size-xl: 18px;         /* 标题文本 */
--font-size-2xl: 20px;        /* 大标题 */

/* 字重 */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### 4. 间距系统

**基础间距单位**
```css
/* 8px基础网格系统 */
--spacing-xs: 4px;            /* 0.5单位 */
--spacing-sm: 8px;            /* 1单位 */
--spacing-md: 16px;           /* 2单位 */
--spacing-lg: 24px;           /* 3单位 */
--spacing-xl: 32px;           /* 4单位 */
--spacing-2xl: 48px;          /* 6单位 */
--spacing-3xl: 64px;          /* 8单位 */
```

**组件间距**
```css
/* 组件内部间距 */
--padding-xs: 4px 8px;
--padding-sm: 8px 12px;
--padding-md: 12px 16px;
--padding-lg: 16px 24px;

/* 组件外部间距 */
--margin-component: 16px;     /* 组件间距 */
--margin-section: 32px;       /* 区块间距 */
```

### 5. 圆角和阴影

**圆角系统**
```css
--radius-xs: 2px;             /* 小圆角 */
--radius-sm: 4px;             /* 标准圆角 */
--radius-md: 6px;             /* 中等圆角 */
--radius-lg: 8px;             /* 大圆角 */
--radius-full: 50%;           /* 圆形 */
```

**阴影系统**
```css
/* 层级阴影 */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.1);
--shadow-md: 0 2px 4px rgba(0, 0, 0, 0.15);
--shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.2);
--shadow-xl: 0 8px 16px rgba(0, 0, 0, 0.25);

/* 特殊阴影 */
--shadow-focus: 0 0 0 2px rgba(0, 122, 204, 0.3);
--shadow-error: 0 0 0 2px rgba(244, 67, 54, 0.3);
```

## 布局设计

### 1. 整体布局结构

**主要区域划分**
```
┌─────────────────────────────────────────────────────────────┐
│                        顶部工具栏                            │
├─────────────┬─────────────────────────────┬─────────────────┤
│             │                             │                 │
│   文件      │                             │    属性面板     │
│   管理器    │        代码编辑区域          │   (可折叠)      │
│             │                             │                 │
│             │                             │                 │
├─────────────┼─────────────────────────────┤                 │
│   指标      │                             │                 │
│   库面板    │        预览/输出区域         │                 │
│  (可折叠)   │                             │                 │
└─────────────┴─────────────────────────────┴─────────────────┘
│                        状态栏                               │
└─────────────────────────────────────────────────────────────┘
```

**响应式布局断点**
```css
/* 断点定义 */
--breakpoint-sm: 768px;       /* 平板 */
--breakpoint-md: 1024px;      /* 小桌面 */
--breakpoint-lg: 1440px;      /* 大桌面 */
--breakpoint-xl: 1920px;      /* 超大屏 */

/* 布局尺寸 */
--sidebar-width: 280px;       /* 侧边栏宽度 */
--sidebar-min-width: 200px;   /* 侧边栏最小宽度 */
--toolbar-height: 48px;       /* 工具栏高度 */
--statusbar-height: 24px;     /* 状态栏高度 */
```

### 2. 顶部工具栏设计

**工具栏布局**
```
┌─────────────────────────────────────────────────────────────┐
│ [Logo] [新建▼] [打开] [保存] │ [编译] [运行] │ [设置] [帮助] │
└─────────────────────────────────────────────────────────────┘
```

**工具栏组件规范**
- **高度**: 48px
- **背景色**: `--bg-secondary`
- **边框**: 底部1px `--border-primary`
- **按钮间距**: 8px
- **按钮尺寸**: 32x32px
- **图标尺寸**: 16x16px

**按钮状态设计**
```css
/* 默认状态 */
.toolbar-button {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

/* 悬停状态 */
.toolbar-button:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}

/* 激活状态 */
.toolbar-button:active,
.toolbar-button.active {
  background: var(--accent-primary);
  color: var(--text-inverse);
}

/* 禁用状态 */
.toolbar-button:disabled {
  color: var(--text-disabled);
  cursor: not-allowed;
}
```

### 3. 侧边栏设计

#### 3.1 文件管理器

**文件树结构**
```
📁 indicators/
├── 📁 main-chart/
│   ├── 📄 custom-ma.dsl
│   ├── 📄 bollinger-bands.dsl
│   └── 📄 ichimoku.dsl
├── 📁 sub-chart/
│   ├── 📄 custom-rsi.dsl
│   ├── 📄 macd.dsl
│   └── 📄 stochastic.dsl
└── 📁 templates/
    ├── 📄 main-chart-template.dsl
    └── 📄 sub-chart-template.dsl
```

**文件项设计规范**
```css
/* 文件项容器 */
.file-item {
  height: 32px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  border-radius: var(--radius-sm);
}

/* 文件项状态 */
.file-item:hover {
  background: var(--surface-hover);
}

.file-item.selected {
  background: var(--accent-primary);
  color: var(--text-inverse);
}

.file-item.modified::after {
  content: '●';
  color: var(--warning);
  margin-left: auto;
}
```

**文件图标系统**
```css
/* 文件类型图标 */
.file-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
}

/* DSL文件图标 */
.file-icon.dsl {
  background: url('icons/dsl-file.svg');
  filter: hue-rotate(210deg); /* 蓝色调 */
}

/* JavaScript文件图标 */
.file-icon.js {
  background: url('icons/js-file.svg');
  filter: hue-rotate(60deg); /* 黄色调 */
}

/* 文件夹图标 */
.folder-icon {
  background: url('icons/folder.svg');
  filter: hue-rotate(30deg); /* 橙色调 */
}
```

#### 3.2 指标库面板

**指标分类展示**
```
📊 内置指标库
├── 📈 趋势指标
│   ├── SMA - 简单移动平均
│   ├── EMA - 指数移动平均
│   ├── MACD - 移动平均收敛发散
│   └── Bollinger Bands - 布林带
├── 📊 震荡指标
│   ├── RSI - 相对强弱指数
│   ├── Stochastic - 随机指标
│   └── Williams %R - 威廉指标
└── 📉 成交量指标
    ├── Volume - 成交量
    ├── OBV - 能量潮
    └── VWAP - 成交量加权平均价
```

**指标项设计**
```css
/* 指标项布局 */
.indicator-item {
  padding: 12px;
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
  background: var(--bg-tertiary);
}

.indicator-item:hover {
  border-color: var(--accent-primary);
  background: var(--surface-primary);
}

/* 指标信息布局 */
.indicator-header {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

.indicator-name {
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.indicator-shortname {
  margin-left: auto;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  background: var(--surface-secondary);
  padding: 2px 6px;
  border-radius: var(--radius-xs);
}

.indicator-description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.4;
}
```

### 4. 主编辑区域设计

#### 4.1 代码编辑器

**Monaco Editor集成设计**
```css
/* 编辑器容器 */
.code-editor {
  height: 100%;
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

/* 编辑器主题配置 */
.monaco-editor {
  --editor-background: var(--bg-primary);
  --editor-foreground: var(--text-primary);
  --editor-selection-background: rgba(0, 122, 204, 0.3);
  --editor-line-highlight: var(--bg-secondary);
  --editor-cursor: var(--accent-primary);
}
```

**行号和折叠区域**
```css
/* 行号区域 */
.monaco-editor .margin {
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-primary);
}

.monaco-editor .line-numbers {
  color: var(--text-disabled);
  font-size: var(--font-size-xs);
}

/* 当前行高亮 */
.monaco-editor .current-line {
  background: var(--bg-tertiary);
  border: none;
}

/* 代码折叠 */
.monaco-editor .folding-decoration {
  color: var(--text-secondary);
}
```

**错误和警告标记**
```css
/* 错误波浪线 */
.monaco-editor .squiggly-error {
  border-bottom: 2px wavy var(--error);
}

/* 警告波浪线 */
.monaco-editor .squiggly-warning {
  border-bottom: 2px wavy var(--warning);
}

/* 信息提示 */
.monaco-editor .squiggly-info {
  border-bottom: 2px wavy var(--info);
}
```

#### 4.2 智能提示设计

**自动补全面板**
```css
/* 补全建议容器 */
.suggest-widget {
  background: var(--surface-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 300px;
  overflow-y: auto;
}

/* 建议项 */
.suggest-item {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.suggest-item:hover,
.suggest-item.focused {
  background: var(--surface-hover);
}

.suggest-item.selected {
  background: var(--accent-primary);
  color: var(--text-inverse);
}
```

**建议项内容布局**
```css
/* 图标 */
.suggest-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  flex-shrink: 0;
}

/* 函数图标 */
.suggest-icon.function {
  background: url('icons/function.svg');
  filter: hue-rotate(270deg); /* 紫色 */
}

/* 变量图标 */
.suggest-icon.variable {
  background: url('icons/variable.svg');
  filter: hue-rotate(210deg); /* 蓝色 */
}

/* 关键字图标 */
.suggest-icon.keyword {
  background: url('icons/keyword.svg');
  filter: hue-rotate(300deg); /* 粉色 */
}

/* 建议文本 */
.suggest-label {
  flex: 1;
  font-weight: var(--font-weight-medium);
}

.suggest-detail {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-left: 12px;
}
```

#### 4.3 错误面板设计

**错误列表布局**
```css
/* 错误面板容器 */
.error-panel {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-primary);
  max-height: 200px;
  overflow-y: auto;
}

/* 错误项 */
.error-item {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-secondary);
  display: flex;
  align-items: flex-start;
  cursor: pointer;
}

.error-item:hover {
  background: var(--surface-hover);
}

.error-item:last-child {
  border-bottom: none;
}
```

**错误信息展示**
```css
/* 错误级别图标 */
.error-severity {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  margin-top: 2px;
  flex-shrink: 0;
}

.error-severity.error {
  background: url('icons/error.svg');
  filter: hue-rotate(0deg); /* 红色 */
}

.error-severity.warning {
  background: url('icons/warning.svg');
  filter: hue-rotate(30deg); /* 橙色 */
}

.error-severity.info {
  background: url('icons/info.svg');
  filter: hue-rotate(210deg); /* 蓝色 */
}

/* 错误信息文本 */
.error-message {
  flex: 1;
  font-size: var(--font-size-sm);
  line-height: 1.4;
}

.error-location {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-top: 2px;
}
```

### 5. 预览区域设计

#### 5.1 编译结果预览

**预览面板布局**
```css
/* 预览容器 */
.preview-panel {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 预览头部 */
.preview-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.preview-title {
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

/* 预览内容 */
.preview-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
}
```

**代码预览样式**
```css
/* 生成代码显示 */
.generated-code {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  padding: 16px;
  font-family: var(--font-family-mono);
  font-size: var(--font-size-sm);
  line-height: 1.5;
  overflow-x: auto;
}

/* 代码语法高亮 */
.generated-code .keyword {
  color: var(--code-keyword);
  font-weight: var(--font-weight-medium);
}

.generated-code .string {
  color: var(--code-string);
}

.generated-code .number {
  color: var(--code-number);
}

.generated-code .comment {
  color: var(--code-comment);
  font-style: italic;
}
```

#### 5.2 编译状态指示

**状态指示器设计**
```css
/* 编译状态容器 */
.compile-status {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
}

/* 成功状态 */
.compile-status.success {
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid var(--success);
  color: var(--success);
}

/* 错误状态 */
.compile-status.error {
  background: rgba(244, 67, 54, 0.1);
  border: 1px solid var(--error);
  color: var(--error);
}

/* 编译中状态 */
.compile-status.compiling {
  background: rgba(33, 150, 243, 0.1);
  border: 1px solid var(--info);
  color: var(--info);
}

/* 状态图标 */
.status-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
}

/* 旋转动画（编译中） */
.status-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### 6. 属性面板设计

#### 6.1 指标参数配置

**参数面板布局**
```css
/* 属性面板容器 */
.properties-panel {
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-primary);
  width: 300px;
  min-width: 250px;
  max-width: 400px;
  resize: horizontal;
  overflow: hidden;
}

/* 面板头部 */
.properties-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 面板内容 */
.properties-content {
  padding: 16px;
  overflow-y: auto;
  height: calc(100% - 48px);
}
```

**参数组设计**
```css
/* 参数组 */
.param-group {
  margin-bottom: 24px;
}

.param-group-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

/* 参数项 */
.param-item {
  margin-bottom: 16px;
}

.param-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  margin-bottom: 6px;
}

.param-description {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-bottom: 8px;
  line-height: 1.4;
}
```

**输入控件设计**
```css
/* 数字输入框 */
.number-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.number-input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-focus);
}

/* 颜色选择器 */
.color-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-preview {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-secondary);
  cursor: pointer;
}

.color-input {
  flex: 1;
  padding: 6px 8px;
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-family: var(--font-family-mono);
  font-size: var(--font-size-xs);
}

/* 下拉选择器 */
.select-input {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.select-input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-focus);
}
```

#### 6.2 指标信息展示

**指标信息卡片**
```css
/* 信息卡片 */
.info-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 16px;
}

.info-card-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin-bottom: 8px;
}

.info-card-content {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 指标统计 */
.indicator-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: var(--surface-primary);
  border-radius: var(--radius-sm);
}

.stat-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--accent-primary);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  margin-top: 2px;
}
```

### 7. 状态栏设计

**状态栏布局**
```css
/* 状态栏容器 */
.status-bar {
  height: 24px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-primary);
  display: flex;
  align-items: center;
  padding: 0 16px;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* 状态项 */
.status-item {
  display: flex;
  align-items: center;
  margin-right: 16px;
  cursor: pointer;
}

.status-item:hover {
  color: var(--text-primary);
}

.status-item:last-child {
  margin-left: auto;
  margin-right: 0;
}

/* 状态图标 */
.status-icon {
  width: 12px;
  height: 12px;
  margin-right: 4px;
}
```

**状态信息展示**
```css
/* 文件状态 */
.file-status {
  display: flex;
  align-items: center;
}

.file-status.modified {
  color: var(--warning);
}

.file-status.saved {
  color: var(--success);
}

/* 编译状态 */
.compile-status-bar {
  display: flex;
  align-items: center;
}

.compile-status-bar.success {
  color: var(--success);
}

.compile-status-bar.error {
  color: var(--error);
}

/* 光标位置 */
.cursor-position {
  font-family: var(--font-family-mono);
}

/* 编码信息 */
.encoding-info {
  text-transform: uppercase;
}
```

## 交互设计

### 1. 鼠标交互

**悬停效果**
```css
/* 通用悬停效果 */
.interactive-element {
  transition: all 0.2s ease;
  cursor: pointer;
}

.interactive-element:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 按钮悬停 */
.button:hover {
  background: var(--surface-hover);
  border-color: var(--accent-primary);
}

/* 文件项悬停 */
.file-item:hover {
  background: var(--surface-hover);
  padding-left: 16px;
}
```

**点击反馈**
```css
/* 点击动画 */
.clickable {
  transition: transform 0.1s ease;
}

.clickable:active {
  transform: scale(0.98);
}

/* 涟漪效果 */
.ripple-effect {
  position: relative;
  overflow: hidden;
}

.ripple-effect::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.ripple-effect:active::after {
  width: 200px;
  height: 200px;
}
```

### 2. 键盘导航

**焦点样式**
```css
/* 焦点指示器 */
.focusable:focus {
  outline: none;
  box-shadow: var(--shadow-focus);
  border-color: var(--accent-primary);
}

/* 跳过链接 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--accent-primary);
  color: var(--text-inverse);
  padding: 8px;
  text-decoration: none;
  border-radius: var(--radius-sm);
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

**键盘快捷键提示**
```css
/* 快捷键标签 */
.keyboard-shortcut {
  font-size: var(--font-size-xs);
  color: var(--text-disabled);
  background: var(--surface-secondary);
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  font-family: var(--font-family-mono);
  margin-left: auto;
}

/* 快捷键组合 */
.key-combo {
  display: inline-flex;
  gap: 2px;
}

.key {
  background: var(--surface-primary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-xs);
  padding: 1px 4px;
  font-size: var(--font-size-xs);
  min-width: 16px;
  text-align: center;
}
```

### 3. 拖拽交互

**拖拽样式**
```css
/* 可拖拽元素 */
.draggable {
  cursor: grab;
}

.draggable:active {
  cursor: grabbing;
}

.draggable.dragging {
  opacity: 0.7;
  transform: rotate(5deg);
  z-index: 1000;
}

/* 拖拽目标区域 */
.drop-zone {
  border: 2px dashed var(--border-secondary);
  border-radius: var(--radius-md);
  padding: 16px;
  text-align: center;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.drop-zone.drag-over {
  border-color: var(--accent-primary);
  background: rgba(0, 122, 204, 0.1);
  color: var(--accent-primary);
}

.drop-zone.drop-valid {
  border-color: var(--success);
  background: rgba(76, 175, 80, 0.1);
  color: var(--success);
}
```

### 4. 加载状态

**加载指示器**
```css
/* 骨架屏 */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--surface-secondary) 25%,
    var(--surface-hover) 50%,
    var(--surface-secondary) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 加载旋转器 */
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-secondary);
  border-top: 2px solid var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 进度条 */
.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--surface-secondary);
  border-radius: var(--radius-xs);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-primary);
  border-radius: var(--radius-xs);
  transition: width 0.3s ease;
}
```

## 响应式设计

### 1. 断点策略

**布局适配**
```css
/* 大屏幕 (≥1440px) */
@media (min-width: 1440px) {
  .main-layout {
    grid-template-columns: 300px 1fr 320px;
  }
  
  .sidebar {
    width: 300px;
  }
  
  .properties-panel {
    width: 320px;
  }
}

/* 中等屏幕 (1024px - 1439px) */
@media (min-width: 1024px) and (max-width: 1439px) {
  .main-layout {
    grid-template-columns: 280px 1fr 280px;
  }
  
  .sidebar {
    width: 280px;
  }
  
  .properties-panel {
    width: 280px;
  }
}

/* 小屏幕 (768px - 1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-layout {
    grid-template-columns: 250px 1fr;
  }
  
  .properties-panel {
    position: absolute;
    right: 0;
    top: 48px;
    height: calc(100vh - 72px);
    transform: translateX(100%);
    transition: transform 0.3s ease;
  }
  
  .properties-panel.open {
    transform: translateX(0);
  }
}

/* 移动设备 (<768px) */
@media (max-width: 767px) {
  .main-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }
  
  .sidebar {
    position: fixed;
    left: 0;
    top: 48px;
    height: calc(100vh - 72px);
    width: 280px;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 100;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .properties-panel {
    display: none;
  }
}
```

### 2. 触摸优化

**触摸目标尺寸**
```css
/* 移动端触摸目标 */
@media (max-width: 767px) {
  .toolbar-button {
    min-width: 44px;
    min-height: 44px;
  }
  
  .file-item {
    min-height: 44px;
    padding: 0 16px;
  }
  
  .tab-button {
    min-height: 44px;
    padding: 0 20px;
  }
}

/* 触摸手势支持 */
.touch-scroll {
  -webkit-overflow-scrolling: touch;
  overflow-scrolling: touch;
}

.pinch-zoom {
  touch-action: pinch-zoom;
}
```

### 3. 自适应字体

**字体缩放**
```css
/* 基础字体大小 */
html {
  font-size: 14px;
}

/* 大屏幕字体放大 */
@media (min-width: 1440px) {
  html {
    font-size: 15px;
  }
}

/* 小屏幕字体缩小 */
@media (max-width: 767px) {
  html {
    font-size: 13px;
  }
}

/* 高DPI屏幕优化 */
@media (-webkit-min-device-pixel-ratio: 2) {
  .icon {
    image-rendering: -webkit-optimize-contrast;
  }
}
```

## 动画设计

### 1. 过渡动画

**基础过渡**
```css
/* 全局过渡设置 */
* {
  transition-duration: 0.2s;
  transition-timing-function: ease;
}

/* 快速过渡 */
.transition-fast {
  transition-duration: 0.1s;
}

/* 慢速过渡 */
.transition-slow {
  transition-duration: 0.3s;
}

/* 弹性过渡 */
.transition-bounce {
  transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

**页面切换动画**
```css
/* 淡入淡出 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滑动切换 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}
```

### 2. 微交互动画

**按钮动画**
```css
/* 按钮点击动画 */
@keyframes button-press {
  0% { transform: scale(1); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}

.button:active {
  animation: button-press 0.1s ease;
}

/* 成功反馈动画 */
@keyframes success-pulse {
  0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
  100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
}

.success-feedback {
  animation: success-pulse 0.6s ease;
}
```

**加载动画**
```css
/* 脉冲加载 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.loading-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

/* 波浪加载 */
@keyframes wave {
  0%, 60%, 100% { transform: initial; }
  30% { transform: translateY(-15px); }
}

.loading-wave {
  display: inline-block;
  animation: wave 1.3s ease-in-out infinite;
}

.loading-wave:nth-child(2) { animation-delay: -1.1s; }
.loading-wave:nth-child(3) { animation-delay: -0.9s; }
```

## 可访问性设计

### 1. 颜色对比度

**对比度标准**
```css
/* 确保文本对比度符合WCAG AA标准 */
/* 正常文本: 4.5:1 */
/* 大文本: 3:1 */

/* 高对比度模式 */
@media (prefers-contrast: high) {
  :root {
    --text-primary: #ffffff;
    --text-secondary: #e0e0e0;
    --bg-primary: #000000;
    --bg-secondary: #1a1a1a;
    --border-primary: #666666;
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 2. 屏幕阅读器支持

**ARIA标签**
```html
<!-- 主要区域标记 -->
<main role="main" aria-label="代码编辑器">
  <section aria-label="文件管理器" role="navigation">
    <!-- 文件树 -->
  </section>
  
  <section aria-label="代码编辑区域" role="textbox" aria-multiline="true">
    <!-- Monaco编辑器 -->
  </section>
  
  <aside aria-label="属性面板" role="complementary">
    <!-- 属性配置 -->
  </aside>
</main>

<!-- 状态信息 -->
<div role="status" aria-live="polite" id="compile-status">
  编译成功
</div>

<!-- 错误信息 -->
<div role="alert" aria-live="assertive" id="error-messages">
  <!-- 错误列表 -->
</div>
```

**键盘导航**
```css
/* Tab顺序优化 */
.tab-sequence {
  tab-index: 0;
}

.skip-tab {
  tab-index: -1;
}

/* 焦点陷阱 */
.modal-open {
  overflow: hidden;
}

.modal-open .main-content {
  filter: blur(2px);
  pointer-events: none;
}
```

## 性能优化

### 1. CSS优化

**关键CSS内联**
```css
/* 关键渲染路径CSS */
.critical-css {
  /* 首屏必需的样式 */
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  background: #1e1e1e;
  color: #cccccc;
}

/* 非关键CSS延迟加载 */
.non-critical {
  /* 非首屏样式 */
}
```

**CSS变量优化**
```css
/* 减少重复计算 */
:root {
  --computed-height: calc(100vh - 72px);
  --sidebar-width: 280px;
}

.sidebar {
  width: var(--sidebar-width);
  height: var(--computed-height);
}
```

### 2. 渲染优化

**GPU加速**
```css
/* 启用硬件加速 */
.gpu-accelerated {
  transform: translateZ(0);
  will-change: transform;
}

/* 动画优化 */
.smooth-animation {
  transform: translate3d(0, 0, 0);
  backface-visibility: hidden;
}
```

**重排重绘优化**
```css
/* 避免触发重排的属性 */
.no-reflow {
  /* 使用transform代替left/top */
  transform: translateX(100px);
  
  /* 使用opacity代替visibility */
  opacity: 0;
}

/* 合成层优化 */
.composite-layer {
  position: relative;
  z-index: 0;
  transform: translateZ(0);
}
```

## 主题系统

### 1. 主题切换

**主题变量定义**
```css
/* 深色主题（默认） */
[data-theme="dark"] {
  --bg-primary: #1e1e1e;
  --bg-secondary: #252526;
  --text-primary: #cccccc;
  --text-secondary: #969696;
  --accent-primary: #007acc;
}

/* 浅色主题 */
[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f8f8;
  --text-primary: #333333;
  --text-secondary: #666666;
  --accent-primary: #0066cc;
}

/* 高对比度主题 */
[data-theme="high-contrast"] {
  --bg-primary: #000000;
  --bg-secondary: #1a1a1a;
  --text-primary: #ffffff;
  --text-secondary: #e0e0e0;
  --accent-primary: #ffff00;
}
```

**主题切换动画**
```css
/* 主题切换过渡 */
* {
  transition: background-color 0.3s ease,
              color 0.3s ease,
              border-color 0.3s ease;
}

/* 主题切换器 */
.theme-switcher {
  display: flex;
  background: var(--surface-primary);
  border-radius: var(--radius-lg);
  padding: 4px;
}

.theme-option {
  padding: 8px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-option.active {
  background: var(--accent-primary);
  color: var(--text-inverse);
}
```

### 2. 自定义主题

**主题编辑器**
```css
/* 颜色选择面板 */
.color-palette {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
  padding: 16px;
}

.color-swatch {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-swatch:hover {
  transform: scale(1.1);
  border-color: var(--text-primary);
}

.color-swatch.selected {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px var(--accent-primary);
}
```

## 图标系统

### 1. 图标规范

**图标尺寸**
```css
/* 图标尺寸标准 */
.icon-xs { width: 12px; height: 12px; }
.icon-sm { width: 16px; height: 16px; }
.icon-md { width: 20px; height: 20px; }
.icon-lg { width: 24px; height: 24px; }
.icon-xl { width: 32px; height: 32px; }

/* 图标基础样式 */
.icon {
  display: inline-block;
  vertical-align: middle;
  fill: currentColor;
  flex-shrink: 0;
}

/* 图标状态 */
.icon-interactive {
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-interactive:hover {
  transform: scale(1.1);
  opacity: 0.8;
}
```

**SVG图标优化**
```css
/* SVG图标样式 */
.svg-icon {
  width: 1em;
  height: 1em;
  fill: currentColor;
  display: inline-block;
  vertical-align: -0.125em;
}

/* 图标颜色变体 */
.icon-primary { color: var(--accent-primary); }
.icon-success { color: var(--success); }
.icon-warning { color: var(--warning); }
.icon-error { color: var(--error); }
.icon-muted { color: var(--text-disabled); }
```

### 2. 图标库

**常用图标定义**
```html
<!-- 文件操作图标 -->
<svg class="icon icon-file">
  <use href="#icon-file"></use>
</svg>

<svg class="icon icon-folder">
  <use href="#icon-folder"></use>
</svg>

<svg class="icon icon-save">
  <use href="#icon-save"></use>
</svg>

<!-- 编辑操作图标 -->
<svg class="icon icon-copy">
  <use href="#icon-copy"></use>
</svg>

<svg class="icon icon-paste">
  <use href="#icon-paste"></use>
</svg>

<svg class="icon icon-undo">
  <use href="#icon-undo"></use>
</svg>

<!-- 编译运行图标 -->
<svg class="icon icon-play">
  <use href="#icon-play"></use>
</svg>

<svg class="icon icon-compile">
  <use href="#icon-compile"></use>
</svg>

<svg class="icon icon-stop">
  <use href="#icon-stop"></use>
</svg>
```

## 组件库设计

### 1. 按钮组件

**基础按钮**
```css
/* 按钮基础样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 16px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

/* 按钮尺寸 */
.btn-sm {
  padding: 6px 12px;
  font-size: var(--font-size-xs);
  min-height: 28px;
}

.btn-md {
  padding: 8px 16px;
  font-size: var(--font-size-sm);
  min-height: 32px;
}

.btn-lg {
  padding: 12px 24px;
  font-size: var(--font-size-base);
  min-height: 40px;
}
```

**按钮变体**
```css
/* 主要按钮 */
.btn-primary {
  background: var(--accent-primary);
  color: var(--text-inverse);
  border-color: var(--accent-primary);
}

.btn-primary:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
}

/* 次要按钮 */
.btn-secondary {
  background: var(--surface-primary);
  color: var(--text-primary);
  border-color: var(--border-primary);
}

.btn-secondary:hover {
  background: var(--surface-hover);
  border-color: var(--accent-primary);
}

/* 危险按钮 */
.btn-danger {
  background: var(--error);
  color: var(--text-inverse);
  border-color: var(--error);
}

.btn-danger:hover {
  background: #d32f2f;
  border-color: #d32f2f;
}

/* 幽灵按钮 */
.btn-ghost {
  background: transparent;
  color: var(--text-primary);
  border-color: var(--border-primary);
}

.btn-ghost:hover {
  background: var(--surface-hover);
  color: var(--accent-primary);
  border-color: var(--accent-primary);
}
```

### 2. 输入组件

**文本输入框**
```css
/* 输入框基础样式 */
.input {
  width: 100%;
  padding: 8px 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-focus);
}

.input:disabled {
  background: var(--surface-secondary);
  color: var(--text-disabled);
  cursor: not-allowed;
}

.input.error {
  border-color: var(--error);
  box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.2);
}

/* 输入框尺寸 */
.input-sm {
  padding: 6px 10px;
  font-size: var(--font-size-xs);
}

.input-lg {
  padding: 12px 16px;
  font-size: var(--font-size-base);
}
```

**输入组合**
```css
/* 输入组 */
.input-group {
  display: flex;
  width: 100%;
}

.input-group .input {
  border-radius: 0;
  border-right: none;
}

.input-group .input:first-child {
  border-top-left-radius: var(--radius-sm);
  border-bottom-left-radius: var(--radius-sm);
}

.input-group .input:last-child {
  border-top-right-radius: var(--radius-sm);
  border-bottom-right-radius: var(--radius-sm);
  border-right: 1px solid var(--border-secondary);
}

/* 输入前缀/后缀 */
.input-addon {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: var(--surface-secondary);
  border: 1px solid var(--border-secondary);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  white-space: nowrap;
}

.input-addon:first-child {
  border-right: none;
  border-top-left-radius: var(--radius-sm);
  border-bottom-left-radius: var(--radius-sm);
}

.input-addon:last-child {
  border-left: none;
  border-top-right-radius: var(--radius-sm);
  border-bottom-right-radius: var(--radius-sm);
}
```

### 3. 模态框组件

**模态框结构**
```css
/* 模态框遮罩 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.modal-overlay.open {
  opacity: 1;
  visibility: visible;
}

/* 模态框容器 */
.modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  transform: scale(0.9) translateY(-20px);
  transition: all 0.3s ease;
}

.modal-overlay.open .modal {
  transform: scale(1) translateY(0);
}

/* 模态框头部 */
.modal-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border-secondary);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}

/* 模态框内容 */
.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
}

.modal-footer {
  padding: 16px 24px 20px;
  border-top: 1px solid var(--border-secondary);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
```

### 4. 通知组件

**通知容器**
```css
/* 通知容器 */
.notification-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1100;
  max-width: 400px;
  pointer-events: none;
}

/* 通知项 */
.notification {
  background: var(--surface-primary);
  border: 1px solid var(--border-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  pointer-events: auto;
  transform: translateX(100%);
  transition: all 0.3s ease;
}

.notification.show {
  transform: translateX(0);
}

.notification.hide {
  transform: translateX(100%);
  opacity: 0;
}

/* 通知类型 */
.notification.success {
  border-left: 4px solid var(--success);
}

.notification.warning {
  border-left: 4px solid var(--warning);
}

.notification.error {
  border-left: 4px solid var(--error);
}

.notification.info {
  border-left: 4px solid var(--info);
}

/* 通知内容 */
.notification-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
  margin-top: 2px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin-bottom: 4px;
}

.notification-message {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.4;
}

.notification-close {
  background: none;
  border: none;
  color: var(--text-disabled);
  cursor: pointer;
  padding: 2px;
  margin-left: 8px;
  border-radius: var(--radius-xs);
  transition: all 0.2s ease;
}

.notification-close:hover {
  background: var(--surface-hover);
  color: var(--text-secondary);
}
```

## 输出要求

### 1. 设计交付物

**必需交付物**
1. **设计系统文档** - 完整的设计规范和组件库
2. **界面原型** - 高保真界面设计稿
3. **交互原型** - 可点击的交互演示
4. **组件库** - 可复用的UI组件集合
5. **图标库** - SVG格式的图标资源
6. **设计资源** - 设计源文件和资源包

**可选交付物**
1. **动效演示** - 关键交互动画展示
2. **响应式演示** - 不同屏幕尺寸适配
3. **主题变体** - 多种主题风格展示
4. **可访问性报告** - 无障碍设计验证

### 2. 文件组织结构

**设计文件结构**
```
design/
├── wireframes/              # 线框图
│   ├── desktop/
│   ├── tablet/
│   └── mobile/
├── mockups/                 # 视觉稿
│   ├── light-theme/
│   ├── dark-theme/
│   └── high-contrast/
├── prototypes/              # 交互原型
│   ├── main-flow.fig
│   └── component-demo.fig
├── assets/                  # 设计资源
│   ├── icons/
│   ├── images/
│   └── fonts/
├── components/              # 组件库
│   ├── buttons/
│   ├── inputs/
│   ├── modals/
│   └── notifications/
└── documentation/           # 设计文档
    ├── design-system.md
    ├── component-guide.md
    └── style-guide.md
```

### 3. 设计验收标准

**视觉设计标准**
- [ ] 符合现代化设计趋势
- [ ] 保持视觉一致性
- [ ] 色彩对比度符合WCAG标准
- [ ] 字体层级清晰合理
- [ ] 间距系统规范统一

**交互设计标准**
- [ ] 操作流程直观高效
- [ ] 反馈机制及时明确
- [ ] 错误处理友好易懂
- [ ] 键盘导航完整可用
- [ ] 触摸操作适配良好

**响应式设计标准**
- [ ] 适配主流屏幕尺寸
- [ ] 布局弹性合理
- [ ] 内容优先级明确
- [ ] 交互方式适配设备
- [ ] 性能表现良好

**可访问性标准**
- [ ] 支持屏幕阅读器
- [ ] 键盘导航完整
- [ ] 颜色对比度达标
- [ ] 焦点指示清晰
- [ ] 语义化标记正确

### 4. 开发对接

**设计规范输出**
- CSS变量定义文件
- 组件样式代码
- 图标SVG文件
- 字体文件和配置
- 主题配置文件

**协作流程**
1. 设计评审和确认
2. 设计规范交付
3. 开发实现跟进
4. 视觉还原验收
5. 用户测试反馈
6. 迭代优化改进

---

## 总结

本UI设计提示词为专用指标编程IDE提供了完整的设计指导，涵盖了从整体设计语言到具体组件实现的各个方面。设计以专业性、效率性和现代感为核心，采用深色主题营造专注的开发环境，通过系统化的设计规范确保界面的一致性和可维护性。

**核心设计原则：**
- 功能优先，美观其次
- 一致性贯穿始终
- 响应式适配全面
- 可访问性标准达标
- 性能优化考虑周全

**实施建议：**
1. 优先实现核心界面和关键交互
2. 建立完整的组件库和设计系统
3. 重视用户测试和反馈收集
4. 持续迭代优化用户体验
5. 保持与开发团队的密切协作

通过遵循本设计指导，UI AI将能够创建出专业、高效、美观的指标编程IDE界面，为开发者提供优秀的编程体验。