# 指标板交互逻辑测试指南

## 问题描述
用户反馈："检查指标板，勾选后的交互逻辑，现在是完全错误的"

## 已添加的调试功能

### 1. App.vue 中的调试日志
- 监听 `indicatorState` 的变化
- 当用户勾选/取消勾选指标时，控制台会输出：
  ```
  App.vue - indicatorState changed: { old: {...}, new: {...} }
  ```

### 2. KLineChart.vue 中的调试日志
- 监听 `props.indicators` 的变化
- 当指标状态传递到组件时，控制台会输出：
  ```
  Indicators props changed: {ma: true, vol: true, macd: false}
  ```
- 指标创建/移除时的详细日志：
  ```
  ensureIndicator called: MA, enabled: true
  Creating indicator: MA
  MA indicator created on main pane
  ```

## 测试步骤

### 第一步：基础功能测试
1. 打开浏览器，访问 http://localhost:5173/
2. 打开浏览器开发者工具 (F12)
3. 切换到 Console 标签页
4. 点击顶部工具栏的"指标"按钮
5. 观察是否有初始化日志输出

### 第二步：指标勾选测试
1. 在指标弹窗中，尝试勾选/取消勾选 MA 指标
2. **预期结果**：控制台应该立即显示：
   ```
   App.vue - indicatorState changed: { old: {ma: false, vol: true, macd: false}, new: {ma: true, vol: true, macd: false} }
   ```
3. 如果没有看到上述日志，说明 Vue 的响应式系统有问题

### 第三步：指标传递测试
1. 继续观察控制台
2. **预期结果**：应该看到 KLineChart 组件接收到新的 props：
   ```
   Indicators props changed: {ma: true, vol: true, macd: false}
   ensureIndicator called: MA, enabled: true
   Creating indicator: MA
   MA indicator created on main pane
   ```
3. 如果只看到 App.vue 的日志，没有看到 KLineChart 的日志，说明 props 传递有问题

### 第四步：视觉效果测试
1. 观察 K线图是否有相应的变化
2. MA 指标应该在主图上显示/隐藏
3. VOL 和 MACD 指标应该在副图上显示/隐藏

## 可能的问题及解决方案

### 问题1：没有看到 App.vue 的调试日志
**原因**：Vue 响应式系统没有检测到 indicatorState 的变化
**可能的解决方案**：
- 检查 el-checkbox 的 v-model 绑定是否正确
- 确认 indicatorState 是使用 ref() 创建的响应式对象

### 问题2：看到 App.vue 日志，但没有 KLineChart 日志
**原因**：props 没有正确传递给 KLineChart 组件
**检查点**：
- App.vue 中 KLineChart 组件的 :indicators 属性绑定
- KLineChart 组件的 props 定义

### 问题3：看到所有日志，但指标没有显示
**原因**：KLineCharts 库的 API 调用有问题
**检查点**：
- ensureIndicator 方法的实现
- chart.createIndicator() 和 chart.removeIndicator() 的调用

### 问题4：指标重复创建或状态混乱
**原因**：ensureIndicator 方法的逻辑有问题
**检查点**：
- 是否在创建前正确移除了旧指标
- indicatorVisibility 缓存的管理

## 当前代码分析

### App.vue 中的关键代码
```vue
<!-- 指标弹窗中的复选框 -->
<el-checkbox v-model="indicatorState.ma">MA(移动平均线)</el-checkbox>
<el-checkbox v-model="indicatorState.vol">VOL(成交量)</el-checkbox>
<el-checkbox v-model="indicatorState.macd">MACD</el-checkbox>

<!-- KLineChart 组件调用 -->
<KLineChart :chart-type="chartType" :indicators="indicatorState" />
```

### KLineChart.vue 中的关键代码
```typescript
// Props 定义
const props = defineProps<{
  chartType: 'candle' | 'line'
  indicators?: { ma?: boolean; vol?: boolean; macd?: boolean }
}>()

// Watch 监听器
watch(
  () => props.indicators,
  (val) => {
    console.log('Indicators props changed:', val);
    if (!val) return;
    ensureIndicator('MA', !!val.ma);
    ensureIndicator('VOL', !!val.vol);
    ensureIndicator('MACD', !!val.macd);
  },
  { deep: true, immediate: false }
);
```

## 下一步调试建议

如果按照上述步骤测试后仍有问题，请：

1. **截图控制台输出**：包含所有的调试日志
2. **描述具体现象**：
   - 哪些日志出现了？
   - 哪些日志没有出现？
   - K线图有什么变化？
3. **测试不同指标**：分别测试 MA、VOL、MACD 三个指标
4. **测试不同操作**：勾选、取消勾选、多次切换

## 临时解决方案

如果发现是响应式更新的问题，可以尝试：

1. **强制更新**：在指标弹窗关闭时手动触发更新
2. **使用 nextTick**：确保 DOM 更新后再处理指标
3. **重构 indicatorState**：使用更明确的响应式模式

---

**测试完成后，请将控制台的输出截图发送给开发者，以便进一步诊断问题。**