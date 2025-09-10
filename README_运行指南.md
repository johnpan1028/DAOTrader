# VegaTrader Core MVP 运行指南

这是一个基于vn.py的交易系统MVP，包含FastAPI后端和Vue前端，支持实时K线图表显示。

## 项目结构

```
DAOTrader/
├── backend/                 # FastAPI后端
│   ├── main.py             # 主服务器文件
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── components/
│   │   │   └── KLineChart.vue
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   └── index.html
└── README_运行指南.md
```

## 前置要求

### 1. Python环境
- Python 3.8+
- 推荐使用虚拟环境

### 2. Node.js环境
- Node.js 16+
- npm或yarn

### 3. vn.py安装
```bash
# 克隆vn.py源码
git clone https://github.com/vnpy/vnpy.git
cd vnpy
git checkout v3.9.0

# 以可编辑模式安装
pip install -e .
```

## 启动步骤

### 方法一：使用批处理脚本（Windows）

1. **启动后端**：双击 `start_backend.bat`
2. **启动前端**：双击 `start_frontend.bat`

### 方法二：手动启动

#### 启动后端服务
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

## 验证步骤

1. **检查后端**：
   - 访问 http://localhost:8000/health
   - 应该返回 `{"status": "ok"}`

2. **检查前端**：
   - 访问 http://localhost:5173
   - 打开浏览器开发者工具查看WebSocket连接状态

3. **验证数据流**：
   - 在前端页面应该能看到KLineChart图表
   - 每隔2秒会更新一根新的K线
   - 控制台应该显示WebSocket连接成功

## 功能特性

- ✅ FastAPI后端服务器
- ✅ WebSocket实时通信
- ✅ vn.py事件引擎集成
- ✅ Vue + TypeScript前端
- ✅ KLineChart实时K线图表
- ✅ 模拟数据生成和广播

## 下一步开发

1. 集成真实的市场数据源
2. 添加更多技术指标
3. 实现交易功能
4. 添加用户界面和控制面板
5. 数据持久化存储

## 故障排除

### WebSocket连接失败
- 确保后端服务正在运行
- 检查端口8000是否被占用
- 确认防火墙设置

### vn.py导入错误
- 确保已正确安装vn.py
- 检查Python虚拟环境
- 确认所有依赖已安装

### 前端编译错误
- 确保Node.js版本符合要求
- 删除node_modules重新安装
- 检查TypeScript配置



