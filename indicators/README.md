# 自定义指标库 (Custom Indicators Library)

本文件夹用于存放用户自定义的技术指标，严格遵循KLineChart的自定义指标规范。

## 文件夹结构

```
indicators/
├── README.md           # 说明文档
├── main/              # 主图指标 (显示在K线图上)
│   ├── custom-ma.js   # 自定义移动平均线
│   └── ...
├── sub/               # 副图指标 (显示在独立面板)
│   ├── custom-rsi.js  # 自定义RSI
│   └── ...
└── index.js           # 指标注册入口文件
```

## 指标规范

### 主图指标 (Main Chart Indicators)
- 显示在K线图主面板上
- 通常是价格相关的指标，如移动平均线、布林带等
- 文件命名：`custom-[指标名].js`
- 必须设置 `series: 'price'` 或 `series: 'normal'`

### 副图指标 (Sub Chart Indicators)
- 显示在独立的副图面板中
- 通常是震荡指标或成交量指标，如RSI、MACD、成交量等
- 文件命名：`custom-[指标名].js`
- 必须设置 `series: 'normal'`

## 指标模板结构

每个指标文件必须导出一个符合KLineChart规范的对象：

```javascript
export default {
  name: 'INDICATOR_NAME',        // 指标名称（唯一标识）
  shortName: 'SHORT_NAME',       // 显示名称
  precision: 2,                  // 精度
  calcParams: [14],              // 计算参数
  series: 'normal',              // 'normal' | 'price' | 'volume'
  figures: [                     // 图形配置
    {
      key: 'value',
      title: 'Value: ',
      type: 'line'               // 'line' | 'bar' | 'circle' 等
    }
  ],
  calc: (dataList, indicator) => {
    // 计算逻辑
    return dataList.map(data => ({
      value: data.close  // 示例：返回收盘价
    }));
  }
};
```

## 使用方法

1. 在对应的 `main/` 或 `sub/` 文件夹中创建指标文件
2. 在 `index.js` 中导入并注册指标
3. 前端组件会自动加载并注册所有自定义指标
4. 在图表界面的指标菜单中选择使用

## 注意事项

- 指标名称必须唯一，不能与KLineChart内置指标重复
- 计算函数必须返回与输入数据长度相同的数组
- 主图指标建议使用价格相关的计算
- 副图指标建议使用独立的数值范围
- 所有指标文件必须使用ES6模块语法导出