# 指标显隐功能修复测试指南 v2.0

## 用户反馈的具体问题

> **问题描述**："现在的勾选问题就是，去除勾选，它不会去除指标，而再次勾选，它就重新重复生成指标"

## 针对性修复

### 问题1：取消勾选不移除指标
**根本原因**：
- `chart.removeIndicator({ name })` 可能需要指定 `paneId` 参数
- 缓存的 `indicatorVisibility` 键值可能与实际的 paneId 不匹配

**修复方案**：
```javascript
// 修复前：只按名称移除
chart.removeIndicator({ name });

// 修复后：按paneId逐个移除
keysToRemove.forEach(key => {
  const paneId = key.split(':')[0];
  chart.removeIndicator({ name, paneId });
  indicatorVisibility.delete(key);
});
```

### 问题2：重新勾选重复生成指标
**根本原因**：
- 副图指标创建后无法立即获取准确的 `paneId`
- `indicatorVisibility` 缓存键名不匹配导致重复检查失效

**修复方案**：
```javascript
// 修复前：使用固定的auto_pane前缀
indicatorVisibility.set(`auto_pane:${name}`, true);

// 修复后：尝试获取实际paneId，否则使用临时标识
if (result && result.paneId) {
  indicatorVisibility.set(`${result.paneId}:${name}`, true);
} else {
  indicatorVisibility.set(`temp_pane:${name}`, true);
}
```

## 详细测试步骤

### 🧪 测试环境准备
1. 访问 http://localhost:5173/
2. 打开浏览器开发者工具 (F12)
3. 切换到 Console 标签页
4. 等待 K线图完全加载

### 📋 测试用例1：指标移除功能

#### 步骤1：验证初始状态
- **操作**：观察K线图初始状态
- **预期**：MA显示在主图，VOL显示在副图，MACD不显示

#### 步骤2：测试MA指标移除
1. 点击"指标"按钮打开弹窗
2. **取消勾选 MA 指标**
3. **预期控制台输出**：
   ```
   App.vue - indicatorState changed: { old: {ma: true, vol: true, macd: false}, new: {ma: false, vol: true, macd: false} }
   Indicators props changed: {ma: false, vol: true, macd: false}
   ensureIndicator called: MA, enabled: false
   Removing indicator: MA
   Removing MA from pane: candle_pane
   Indicator MA removal completed
   ```
4. **预期视觉效果**：主图上的MA线应该**完全消失**

#### 步骤3：测试VOL指标移除
1. **取消勾选 VOL 指标**
2. **预期控制台输出**：
   ```
   ensureIndicator called: VOL, enabled: false
   Removing indicator: VOL
   Removing VOL from pane: [实际的paneId]
   Indicator VOL removal completed
   ```
3. **预期视觉效果**：VOL副图面板应该**完全消失**

### 📋 测试用例2：指标重复创建防护

#### 步骤1：重新启用MA指标
1. **重新勾选 MA 指标**
2. **预期控制台输出**：
   ```
   ensureIndicator called: MA, enabled: true
   Creating new indicator: MA
   MA indicator created on main pane, result: [创建结果]
   ```
3. **预期视觉效果**：MA线重新出现在主图

#### 步骤2：测试重复勾选防护
1. 关闭指标弹窗
2. 重新打开指标弹窗
3. **再次勾选已启用的 MA 指标**（应该没有变化）
4. **预期控制台输出**：
   ```
   ensureIndicator called: MA, enabled: true
   Indicator MA already exists, ensuring visibility
   ```
5. **关键验证**：不应该看到 "Creating new indicator" 日志

#### 步骤3：测试MACD指标创建
1. **勾选 MACD 指标**
2. **预期控制台输出**：
   ```
   ensureIndicator called: MACD, enabled: true
   Creating new indicator: MACD
   MACD indicator creation result: [创建结果]
   MACD indicator created on pane: [实际paneId] 或 using temp key
   ```
3. **预期视觉效果**：出现新的MACD副图面板

### 📋 测试用例3：混合操作测试

#### 步骤1：快速切换测试
1. 快速取消勾选VOL → 重新勾选VOL → 再次取消勾选VOL
2. **验证要点**：
   - 每次取消勾选都应该看到 "removal completed" 日志
   - 每次重新勾选都应该正确创建或恢复可见性
   - 不应该出现指标残留或重复创建

#### 步骤2：全部指标操作
1. 同时启用所有指标（MA + VOL + MACD）
2. 同时禁用所有指标
3. **验证要点**：
   - 所有指标都应该正确显示/隐藏
   - 控制台日志应该清晰显示每个操作

## 🔍 问题诊断检查点

### ❌ 如果取消勾选后指标仍然显示
**检查项**：
- [ ] 控制台是否显示 "Removing indicator" 日志？
- [ ] 是否显示 "removal completed" 日志？
- [ ] 是否有错误信息？

**可能原因**：
- `chart.removeIndicator()` API调用失败
- `paneId` 参数不正确
- KLineCharts库版本兼容性问题

### ❌ 如果重新勾选时重复创建指标
**检查项**：
- [ ] 是否看到 "already exists, ensuring visibility" 日志？
- [ ] 还是看到 "Creating new indicator" 日志？
- [ ] `indicatorVisibility` 缓存是否正确？

**可能原因**：
- `existingKeys` 检查逻辑失效
- 缓存键名格式不匹配
- 临时paneId更新机制有问题

### ❌ 如果副图指标行为异常
**检查项**：
- [ ] 创建时是否获取到了实际的 `paneId`？
- [ ] 是否使用了 "temp_pane" 临时标识？
- [ ] tooltip事件是否正确更新了临时键名？

## 🎯 成功标准

### ✅ 指标移除功能正常
- [ ] 取消勾选后指标立即消失
- [ ] 控制台显示完整的移除日志
- [ ] 副图面板在指标移除后消失
- [ ] 不会有指标残留

### ✅ 重复创建防护有效
- [ ] 重新勾选已存在指标时不会重复创建
- [ ] 控制台显示 "already exists" 而非 "Creating new"
- [ ] 指标状态与勾选状态完全同步
- [ ] 性能良好，无不必要的API调用

### ✅ 整体交互流畅
- [ ] 指标弹窗操作响应及时
- [ ] 视觉效果与勾选状态一致
- [ ] 多次操作后状态稳定
- [ ] 控制台日志清晰易懂

## 🚀 高级测试场景

### 场景1：压力测试
- 快速连续点击同一指标的勾选框10次
- 验证是否有内存泄漏或状态混乱

### 场景2：边界情况
- 在K线图加载过程中操作指标
- 在WebSocket连接断开时操作指标

### 场景3：兼容性测试
- 刷新页面后重新测试
- 不同浏览器中测试

---

**如果测试中发现任何问题，请提供：**
1. 具体的操作步骤
2. 控制台完整日志截图
3. 实际视觉效果描述
4. 预期效果与实际效果的差异