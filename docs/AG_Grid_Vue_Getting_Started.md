# AG Grid Vue 快速开始指南

## 概述
AG Grid是一个高性能的Vue数据网格库，用于构建具有无与伦比性能和数百种功能的Vue表格。提供社区版和企业版。

## 快速开始

### 1. NPM安装
安装ag-grid-vue3包，同时也会安装ag-grid-community：
```bash
npm install ag-grid-vue3
```

### 2. 注册模块
注册AllCommunityModule以访问所有社区功能：
```javascript
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';

// 注册所有社区功能
ModuleRegistry.registerModules([AllCommunityModule]);
```

为了最小化包大小，只注册您想要使用的模块。

### 3. 导入Vue数据网格
```javascript
<script>
import { AgGridVue } from "ag-grid-vue3";

export default {
    name: "App",
    components: {
        AgGridVue,
    },
    setup() {},
};
</script>
```

### 4. 定义行和列
```javascript
setup() {
    // 行数据：要显示的数据
    const rowData = ref([
        { make: "Tesla", model: "Model Y", price: 64950, electric: true },
        { make: "Ford", model: "F-Series", price: 33850, electric: false },
        { make: "Toyota", model: "Corolla", price: 29600, electric: false },
    ]);

    // 列定义：定义要显示的列
    const colDefs = ref([
        { field: "make" },
        { field: "model" },
        { field: "price" },
        { field: "electric" }
    ]);

    return {
        rowData,
        colDefs,
    };
},
```

### 5. Vue数据网格组件
将行和列设置为ag-grid-vue组件属性。通过class和style属性应用样式：
```vue
<template>
    <!-- AG Grid组件 -->
    <ag-grid-vue
        :rowData="rowData"
        :columnDefs="colDefs"
        style="height: 500px"
    >
    </ag-grid-vue>
</template>
```

## 主要功能

### 核心功能
- **列管理**：列定义、更新、状态管理、分组、调整大小、移动、固定、跨列
- **行管理**：行数据、排序、编号、跨行、固定、高度、样式、分页、访问、拖拽
- **单元格**：内容、格式化、组件、数据类型、样式、工具提示、表达式
- **过滤**：文本、数字、日期、集合过滤器，自定义过滤器，浮动过滤器
- **选择**：行选择、单元格选择、范围选择
- **编辑**：单元格编辑、批量编辑、撤销/重做、验证

### 高级功能
- **行分组**：数据分组、显示类型、面板、展开/折叠
- **聚合**：列配置、自定义函数、总计行、过滤
- **透视**：结果列、列组、总计
- **树数据**：路径、嵌套记录、自引用记录
- **主从详情**：详情网格、高度、刷新、嵌套
- **服务端数据**：服务端行模型、数据源、配置、排序、过滤

### 图表功能
- **迷你图**：面积图、柱状图、线图
- **集成图表**：范围图表、透视图表、用户创建图表
- **独立图表**：AG Charts

### 导入导出
- **CSV导出**：基本导出功能
- **Excel导出**：样式、公式、额外内容、图片、多工作表

### 主题和样式
- **内置主题**：多种预设主题
- **主题参数**：颜色、字体、边框、紧凑度
- **自定义样式**：CSS扩展、设计系统

### 兼容性
- **浏览器支持**：现代浏览器支持
- **安全性**：安全最佳实践
- **测试**：测试指南和工具

## 企业版功能
企业版包含更多高级功能：
- 高级过滤和分组
- Excel导出
- 服务端行模型
- 主从详情
- 树数据
- 透视和聚合
- 图表集成
- 工具面板

## 安装企业版许可证
如需使用企业版功能，需要安装相应的许可证。

## 迁移指南
提供从旧版本迁移的详细指南和代码模块化工具。

---

*本文档基于AG Grid官方文档整理，用于DAOTrader项目的行情服务中台开发参考。*
*原文档地址：https://www.ag-grid.com/vue-data-grid/getting-started/*
*整理时间：2024年*