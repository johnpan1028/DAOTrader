<template>
  <div ref="chartContainer" :style="containerStyle"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import type { PropType } from 'vue';
import { init, dispose } from 'klinecharts';
// 导入自定义指标库
import { registerCustomIndicators, getMainIndicators, getSubIndicators } from '../../../indicators/index.js';

// 事件：打开指标参数设置
const emit = defineEmits<{
  (e: 'open-indicator-settings', payload: { paneId: string; name: string }): void
}>();

// Props: 图表类型、指标开关和品种代码
const props = defineProps({
  chartType: {
    type: String as PropType<'candle' | 'line'>,
    default: 'candle'
  },
  timeframe: {
    type: String as PropType<'1m' | '5m' | '15m' | '1H' | '2H' | '4H' | 'D' | 'W' | 'M' | 'Y'>,
    default: '15m'
  },
  indicators: {
    type: Object as PropType<{ ma: boolean; vol: boolean; macd: boolean; custom_ma: boolean; custom_rsi: boolean }>,
    default: () => ({ ma: false, vol: false, macd: false, custom_ma: false, custom_rsi: false })
  },
  symbol: {
    type: String,
    default: 'BTCUSDT'
  }
});

const chartContainer = ref<HTMLElement | null>(null);
// 跟踪当前面板ID（用于指标操作）
const tempPaneId = ref<string>('default');
// KLineCharts 原版配色：容器背景
const containerStyle = { width: '100%', height: '100%', backgroundColor: 'transparent' } as const;
let chart: any = null;
let ws: WebSocket | null = null;
let hasInitialData = false;
// 为仅有tick推送的场景做聚合：维护当前时间粒度bar
let currentBar: { timestamp: number; open: number; high: number; low: number; close: number; volume: number } | null = null;
let currentBarTs: number | null = null; // 表示当前聚合桶的开始时间戳(ms)
// 维护每个面板+指标名的可见性，用于tooltip图标的显隐切换
const indicatorVisibility = new Map<string, boolean>();
// ResizeObserver 用于监听容器尺寸变化
let resizeObserver: ResizeObserver | null = null;

// 新增：时间粒度聚合工具
function timeframeToMs(tf: string): number {
  const map: Record<string, number> = {
    '1m': 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '1H': 60 * 60 * 1000,
    '2H': 2 * 60 * 60 * 1000,
    '4H': 4 * 60 * 60 * 1000,
    'D': 24 * 60 * 60 * 1000,
    'W': 7 * 24 * 60 * 60 * 1000,
    'M': 30 * 24 * 60 * 60 * 1000, // 简化按30天处理
    'Y': 365 * 24 * 60 * 60 * 1000 // 简化按365天处理
  };
  return map[tf] ?? 60 * 1000;
}
let aggMs = timeframeToMs(props.timeframe);
function getBucketStart(tsMs: number): number {
  return Math.floor(tsMs / aggMs) * aggMs;
}
function resetAggregation(clearChart = true) {
  hasInitialData = false;
  currentBar = null;
  currentBarTs = null;
  if (chart && clearChart) {
    chart.applyNewData([]);
  }
}
function processIncomingBar(tsMs: number, open: number, high: number, low: number, close: number, volume: number) {
  const bucket = getBucketStart(tsMs);
  if (!chart) return;
  if (!hasInitialData || !currentBar || currentBarTs == null) {
    currentBar = { timestamp: bucket, open, high, low, close, volume: volume ?? 0 };
    chart.applyNewData([currentBar]);
    hasInitialData = true;
    currentBarTs = bucket;
    return;
  }
  if (bucket === currentBarTs) {
    currentBar.high = Math.max(currentBar.high, high);
    currentBar.low = Math.min(currentBar.low, low);
    currentBar.close = close;
    currentBar.volume = (currentBar.volume ?? 0) + (volume ?? 0);
    chart.updateData({ ...currentBar });
  } else if (bucket > currentBarTs) {
    const newBar = { timestamp: bucket, open, high, low, close, volume: volume ?? 0 };
    chart.updateData(newBar);
    currentBar = newBar;
    currentBarTs = bucket;
  } else {
    // 旧数据，忽略
  }
}

// 暴露方法：父组件可调用以应用指标参数
function applyIndicatorCalcParams(payload: { paneId: string; name: string; calcParams: any[] }) {
  if (!chart) return;
  const { paneId, name, calcParams } = payload;
  chart.overrideIndicator({ name, calcParams }, paneId);
}

// 指标显隐控制 - 支持内置指标和自定义指标
const ensureIndicator = (name: 'MA' | 'VOL' | 'MACD' | 'CUSTOM_MA' | 'CUSTOM_RSI', enabled: boolean) => {
  console.log(`ensureIndicator called: ${name}, enabled: ${enabled}`);
  
  const indicator = indicators[name];
  if (!indicator) {
    console.error(`Unknown indicator: ${name}`);
    return;
  }
  
  if (!chart) {
    console.error('Chart not initialized');
    return;
  }
  
  try {
    if (enabled) {
      // 需要显示指标
      if (!indicator.visible) {
        // 创建指标
        console.log(`Creating indicator: ${name}`);
        let id;
        // 根据KLineCharts官方文档，主图指标需要叠加到蜡烛图面板
        if (indicator.isMain) {
          // 主图指标，叠加到蜡烛图面板
          id = chart.createIndicator(indicator.name, true, { id: 'candle_pane' });
        } else {
          // 副图指标，创建独立面板
          id = chart.createIndicator(indicator.name, false);
        }
        indicator.id = id;
        indicator.visible = true;
        
        console.log(`Successfully created ${name} indicator with ID: ${id}`);
      } else {
        console.log(`${name} indicator already visible`);
      }
    } else {
      // 需要隐藏指标
      if (indicator.visible && indicator.id) {
        console.log(`Removing ${name} indicator with ID: ${indicator.id}`);
        chart.removeIndicator(indicator.id);
        indicator.id = null;
        indicator.visible = false;
        
        console.log(`Successfully removed ${name} indicator`);
      } else {
        console.log(`${name} indicator already hidden or ID not found`);
        indicator.visible = false;
        indicator.id = null;
      }
    }
  } catch (error) {
    console.error(`Error in ensureIndicator for ${name}:`, error);
    // 重置状态以保持一致性
    indicator.visible = false;
    indicator.id = null;
  }
  
  console.log(`ensureIndicator ${name} completed, final state: enabled=${enabled}`);
};

// 指标管理对象 - 包含内置指标和自定义指标
const indicators = {
  // 内置指标
  MA: { name: 'MA', visible: false, id: null, isMain: true },
  VOL: { name: 'VOL', visible: false, id: null, isMain: false },
  MACD: { name: 'MACD', visible: false, id: null, isMain: false },
  // 自定义指标
  CUSTOM_MA: { name: 'CUSTOM_MA', visible: false, id: null, isMain: true },
  CUSTOM_RSI: { name: 'CUSTOM_RSI', visible: false, id: null, isMain: false }
};

// 获取所有指标列表（用于指标选择器）
const getAllIndicators = () => {
  const mainIndicators = [
    { name: 'MA', shortName: 'MA', isMain: true, isCustom: false },
    { name: 'CUSTOM_MA', shortName: '自定义MA', isMain: true, isCustom: true }
  ];
  
  const subIndicators = [
    { name: 'VOL', shortName: 'VOL', isMain: false, isCustom: false },
    { name: 'MACD', shortName: 'MACD', isMain: false, isCustom: false },
    { name: 'CUSTOM_RSI', shortName: '自定义RSI', isMain: false, isCustom: true }
  ];
  
  return { mainIndicators, subIndicators };
};

defineExpose({ 
  applyIndicatorCalcParams,
  ensureIndicator,
  getAllIndicators
});

// 根据类型应用图表样式（K线/折线）
const applyChartType = (type: 'candle' | 'line') => {
  if (!chart) return;
  chart.setStyles({
    candle: {
      // 使用 area 作为折线/面积样式，后续可扩展至 ohlc 等类型
      type: type === 'line' ? 'area' : 'candle_solid',
    }
  });
};

// 新增：初始化指标（根据 props.indicators 同步一次）
function initializeIndicators() {
  if (!chart) return;
  try {
    const indi = props.indicators || {} as any;
    Object.entries(indi).forEach(([key, enabled]) => {
      const indicatorName = key.toUpperCase().replace('_', '_');
      ensureIndicator(indicatorName as any, Boolean(enabled));
    });
  } catch (err) {
    console.warn('initializeIndicators error:', err);
  }
}

// 新增：订阅指标相关的交互（占位实现，避免未定义报错）
function subscribeIndicatorToggle() {
  // 目前不绑定额外事件，仅作为占位，后续可根据需要扩展
}

// 注释：defineExpose已在上方处理完成

// 监听indicators属性变化，自动同步指标状态
watch(
  () => props.indicators,
  (newIndicators) => {
    if (!chart) return;
    console.log('KLineChart - indicators props changed:', newIndicators);
    
    // 同步所有指标状态
    Object.entries(newIndicators).forEach(([key, enabled]) => {
      const indicatorName = key.toUpperCase().replace('_', '_'); // MA, VOL, MACD, CUSTOM_MA, CUSTOM_RSI
      ensureIndicator(indicatorName as any, enabled as boolean);
    });
  },
  { deep: true }
);

// 监听品种变化
watch(
  () => props.symbol,
  (newSymbol, oldSymbol) => {
    console.log('KLineChart - Symbol prop changed:', { old: oldSymbol, new: newSymbol });
    console.log('WebSocket state:', ws ? ws.readyState : 'null');
    
    if (newSymbol !== oldSymbol && ws && ws.readyState === WebSocket.OPEN) {
      console.log('Symbol changed from', oldSymbol, 'to', newSymbol);
      
      // 清空图表数据并重置聚合
      if (chart) {
        console.log('Clearing chart data for new symbol');
        chart.applyNewData([]);
        hasInitialData = false;
      }
      currentBar = null;
      currentBarTs = null;
      
      // 订阅新品种的数据
      console.log('Sending subscription for new symbol:', newSymbol);
      ws.send(JSON.stringify({
        type: 'subscribe_symbol',
        symbol: newSymbol
      }));
    } else if (newSymbol !== oldSymbol) {
      console.warn('Cannot subscribe to new symbol - WebSocket not ready:', {
        wsExists: !!ws,
        wsState: ws ? ws.readyState : 'null'
      });
    }
  }
);

// 新增：监听时间粒度变化，重置聚合与数据
watch(
  () => props.timeframe,
  (newTf, oldTf) => {
    console.log('KLineChart - timeframe changed:', { old: oldTf, new: newTf });
    aggMs = timeframeToMs(newTf as string);
    resetAggregation(true);
  }
);

onMounted(async () => {
  // 先初始化WebSocket连接（不依赖图表容器）
  console.log('开始初始化WebSocket连接...');
  
  // 连接WebSocket
  ws = new WebSocket('ws://localhost:8000/ws');
  
  ws.onopen = () => {
    console.log('Connected to WebSocket server');
    // 订阅当前品种的数据
    console.log('Subscribing to symbol:', props.symbol);
    ws?.send(JSON.stringify({
      type: 'subscribe_symbol',
      symbol: props.symbol
    }));
  };
  
  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      console.log('WebSocket message received:', message);
      
      if (message.type === 'bar') {
        const barData = message.data;
        console.log('原始后端数据:', barData);
        
        // 只处理当前选中品种的数据
        if (barData.symbol !== props.symbol) {
          console.log('Ignoring data for different symbol:', barData.symbol, 'current:', props.symbol);
          return;
        }
        
        // 转换数据格式以匹配KLineChart要求
        const tsMs = new Date(barData.datetime).getTime();
        const open = barData.open_price || barData.open;
        const high = barData.high_price || barData.high;
        const low = barData.low_price || barData.low;
        const close = barData.close_price || barData.close;
        const volume = Number(barData.volume ?? 0);
        
        // 统一走聚合逻辑
        processIncomingBar(tsMs, open, high, low, close, volume);
      } else if (message.type === 'tick') {
        const tick = message.data;
        // 只处理当前选中品种
        if (tick.symbol !== props.symbol) {
          return;
        }
        const ts = tick.datetime ? Math.floor(new Date(tick.datetime).getTime()) : Date.now();
        const price = tick.last_price ?? tick.close_price ?? tick.price;
        const vol = Number(tick.volume ?? tick.last_volume ?? 0);
        if (price == null) {
          return;
        }
        if (!chart) {
          // 图表尚未初始化，先不处理（等待图表就绪后由后续数据驱动）
          return;
        }
        // 将tick视为极短周期bar，参与当前时间粒度聚合
        processIncomingBar(ts, price, price, price, price, vol);
      }
    } catch (error) {
      console.error('Error processing message:', error);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket connection closed');
  };
  
  // 然后初始化图表（如果容器存在）
  if (!chartContainer.value) {
    console.warn('图表容器未找到，稍后重试...');
    return;
  }
  
  // 初始化图表
  chart = init(chartContainer.value);
  
  // 注册自定义指标
  try {
    // 导入klinecharts模块用于注册指标
    const klinecharts = await import('klinecharts');
    registerCustomIndicators(klinecharts);
  } catch (err) {
    console.warn('注册自定义指标失败：', err);
  }

  // 应用初始图表类型
  if (props.chartType) {
    applyChartType(props.chartType);
  }

  // 监听容器尺寸变化，自适应图表
  if (chartContainer.value) {
    resizeObserver = new ResizeObserver(() => {
      if (chart && chartContainer.value) {
        // 兼容不同版本的 klinecharts：优先使用 resize，回退到 setSize
        if (typeof (chart as any).resize === 'function') {
          try { (chart as any).resize(); } catch {}
        } else if (typeof (chart as any).setSize === 'function') {
          try { (chart as any).setSize(chartContainer.value!.clientWidth, chartContainer.value!.clientHeight); } catch {}
        }
      }
    });
    resizeObserver.observe(chartContainer.value);
  }

  // 初始化指标（基于当前props.indicators）
  initializeIndicators();

  // 订阅tooltip图标点击事件
  subscribeIndicatorToggle();
});

onUnmounted(() => {
  if (resizeObserver && chartContainer.value) {
    resizeObserver.unobserve(chartContainer.value);
  }
  if (chart) {
    dispose(chart);
    chart = null;
  }
  if (ws) {
    try { ws.close(); } catch {}
    ws = null;
  }
});

</script>
