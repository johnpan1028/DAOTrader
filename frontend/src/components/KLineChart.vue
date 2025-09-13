<template>
  <div ref="chartContainer" :style="containerStyle"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue';
import type { PropType } from 'vue';
import { init, dispose } from 'klinecharts';

// 事件：打开指标参数设置
const emit = defineEmits<{
  (e: 'open-indicator-settings', payload: { paneId: string; name: string }): void
}>();

// Props: 图表类型与指标开关
const props = defineProps({
  chartType: {
    type: String as PropType<'candle' | 'line'>,
    default: 'candle'
  },
  indicators: {
    type: Object as PropType<{ ma: boolean; vol: boolean; macd: boolean }>,
    default: () => ({ ma: true, vol: true, macd: false })
  }
});

const chartContainer = ref<HTMLElement | null>(null);
// 跟踪当前面板ID（用于指标操作）
const tempPaneId = ref<string>('default');
// KLineCharts 原版配色：容器背景
const containerStyle = { width: '100%', height: '100%', backgroundColor: '#131722' } as const;
let chart: any = null;
let ws: WebSocket | null = null;
let hasInitialData = false;
// 维护每个面板+指标名的可见性，用于tooltip图标的显隐切换
const indicatorVisibility = new Map<string, boolean>();

// 暴露方法：父组件可调用以应用指标参数
function applyIndicatorCalcParams(payload: { paneId: string; name: string; calcParams: any[] }) {
  if (!chart) return;
  const { paneId, name, calcParams } = payload;
  chart.overrideIndicator({ name, calcParams }, paneId);
}

defineExpose({ applyIndicatorCalcParams });

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

// 指标管理对象 - 参考测试HTML的成功实现
const indicators = {
  MA: { name: 'MA', visible: false, id: null, isMain: true },
  VOL: { name: 'VOL', visible: false, id: null, isMain: false },
  MACD: { name: 'MACD', visible: false, id: null, isMain: false }
};

// 指标显隐控制 - 使用测试HTML中验证成功的方法
const ensureIndicator = (name: 'MA' | 'VOL' | 'MACD', enabled: boolean) => {
  console.log(`ensureIndicator called: ${name}, enabled: ${enabled}`);
  
  if (!chart) {
    console.warn('Chart not initialized, skipping ensureIndicator');
    return;
  }
  
  const indicator = indicators[name];
  if (!indicator) {
    console.error(`Unknown indicator: ${name}`);
    return;
  }
  
  // 如果状态没有变化，直接返回
  if (enabled === indicator.visible) {
    console.log(`${name} indicator state unchanged, no action needed`);
    return;
  }
  
  try {
    if (enabled) {
      // 添加指标 - 根据官方文档正确设置主图指标
      console.log(`Creating ${name} indicator, isMain: ${indicator.isMain}`);
      let id;
      if (indicator.isMain) {
        // 主图指标需要指定candle_pane
        id = chart.createIndicator(
          indicator.name,
          true,  // isStack参数
          { id: 'candle_pane' }  // 指定主图面板ID
        );
      } else {
        // 副图指标使用默认设置
        id = chart.createIndicator(
          indicator.name,
          false,
          { id: name.toLowerCase() }
        );
      }
      indicator.id = id;
      indicator.visible = true;
      
      console.log(`Successfully created ${name} indicator with ID: ${id}`);
    } else {
      // 移除指标 - 使用测试HTML中的正确方法
      if (indicator.id) {
        console.log(`Removing ${name} indicator with ID: ${indicator.id}`);
        chart.removeIndicator(indicator.id);
        indicator.id = null;
        indicator.visible = false;
        
        console.log(`Successfully removed ${name} indicator`);
      } else {
        console.log(`${name} indicator ID not found, marking as not visible`);
        indicator.visible = false;
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

onMounted(() => {
  if (!chartContainer.value) return;
  
  // 初始化图表
  chart = init(chartContainer.value);
  // 获取CSS变量值（保留，作为后备），但下方将用 LWC 配色统一覆盖
  const rootStyles = getComputedStyle(document.documentElement);
  const borderColor = rootStyles.getPropertyValue('--el-border-color').trim() || '#2a2e39';
  const textSecondary = rootStyles.getPropertyValue('--el-text-color-secondary').trim() || '#5d606b';
  const textRegular = rootStyles.getPropertyValue('--el-text-color-regular').trim() || '#868993';
  const textPrimary = rootStyles.getPropertyValue('--el-text-color-primary').trim() || '#d1d4dc';
  const bgOverlay = rootStyles.getPropertyValue('--el-bg-color-overlay').trim() || '#1e222d';
  const borderLight = rootStyles.getPropertyValue('--el-border-color-light').trim() || '#434651';
  // derive a lighter frame color from the regular text color to soften frame lines
  const frameColor = (() => {
    const c = (textRegular || '#868993').trim();
    const hex = /^#([0-9a-fA-F]{6})$/;
    if (hex.test(c)) {
      const r = parseInt(c.slice(1, 3), 16);
      const g = parseInt(c.slice(3, 5), 16);
      const b = parseInt(c.slice(5, 7), 16);
      const lighten = (v: number, p = 0.28) => Math.min(255, Math.round(v + (255 - v) * p));
      const rr = lighten(r);
      const gg = lighten(g);
      const bb = lighten(b);
      const toHex = (v: number) => v.toString(16).padStart(2, '0');
      return `#${toHex(rr)}${toHex(gg)}${toHex(bb)}`;
    }
    return c; // fallback if not hex
  })();

  // KLineCharts 原版默认配色（与副图保持一致）
  const KLINE_BG = '#131722';
  const KLINE_GRID = '#292929';
  const KLINE_TEXT = '#FFFFFF';
  const KLINE_TEXT_SECONDARY = '#FFFFFF';
  const KLINE_UP = '#2DC08E';     // klinecharts 原版绿色
  const KLINE_DOWN = '#F92855';   // klinecharts 原版红色
  const KLINE_NEUTRAL = '#888888'; // klinecharts 原版灰色
  const KLINE_AREA_LINE = '#1677FF';
  const KLINE_AREA_TOP = 'rgba(22, 119, 255, 0.2)';
  const KLINE_AREA_BOTTOM = 'rgba(22, 119, 255, 0.01)';

  chart.setStyles({
    grid: {
      horizontal: { color: KLINE_GRID },
      vertical: { color: KLINE_GRID }
    },
    xAxis: {
      axisLine: { color: '#333333' },
      tickLine: { color: '#333333' },
      tickText: { color: KLINE_TEXT }
    },
    yAxis: {
      axisLine: { color: '#333333' },
      tickLine: { color: '#333333' },
      tickText: { color: KLINE_TEXT }
    },
    crosshair: {
      horizontal: {
        line: { color: KLINE_TEXT },
        text: { backgroundColor: '#373a40', borderColor: '#373a40', color: KLINE_TEXT }
      },
      vertical: {
        line: { color: KLINE_TEXT },
        text: { backgroundColor: '#373a40', borderColor: '#373a40', color: KLINE_TEXT }
      }
    },
    candle: {
      // 蜡烛颜色（klinecharts 原版配色：绿涨红跌）
      bar: {
        upColor: KLINE_UP,
        downColor: KLINE_DOWN,
        noChangeColor: KLINE_NEUTRAL,
        upBorderColor: KLINE_UP,
        downBorderColor: KLINE_DOWN,
        noChangeBorderColor: KLINE_NEUTRAL,
        upWickColor: KLINE_UP,
        downWickColor: KLINE_DOWN,
        noChangeWickColor: KLINE_NEUTRAL,
      },
      // 折线/面积样式（当类型切为 area 时生效）
      area: {
        lineSize: 2,
        lineColor: KLINE_AREA_LINE,
        value: 'close',
        smooth: false,
        backgroundColor: [
          { offset: 0, color: KLINE_AREA_TOP },
          { offset: 1, color: KLINE_AREA_BOTTOM }
        ],
        point: {
          show: true,
          color: KLINE_AREA_LINE,
          radius: 4,
          rippleColor: 'rgba(22, 119, 255, 0.3)',
          rippleRadius: 8,
          animation: true,
          animationDuration: 1000
        }
      },
      priceMark: {
        last: {
          line: { show: true, style: 'dashed', dashedValue: [4, 4], size: 1 },
          text: { show: true, style: 'fill', color: KLINE_TEXT }
        }
      },
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        rect: { position: 'fixed', borderColor: 'rgba(10, 10, 10, .6)', color: 'rgba(10, 10, 10, .6)' },
        title: { color: KLINE_TEXT },
        legend: { color: KLINE_TEXT },
        icons: [
          {
            id: 'candle_settings',
            position: 'right',
            color: KLINE_TEXT_SECONDARY,
            activeColor: KLINE_TEXT,
            size: 14,
            fontFamily: 'Helvetica Neue',
            icon: '⚙',
            backgroundColor: 'transparent',
            activeBackgroundColor: 'transparent',
            marginLeft: 4,
            marginTop: 2,
            marginRight: 4,
            marginBottom: 2,
            paddingLeft: 2,
            paddingTop: 2,
            paddingRight: 2,
            paddingBottom: 2
          }
        ]
      }
    },
    tooltip: {
      showRule: 'always',
      showType: 'standard',
      rect: { position: 'fixed', borderColor: 'rgba(10, 10, 10, .6)', color: 'rgba(10, 10, 10, .6)' },
      title: { color: KLINE_TEXT },
      legend: { color: KLINE_TEXT }
    },
    indicator: {
      tooltip: {
        showRule: 'always',
        showType: 'standard',
        defaultValue: 'n/a',
        showName: true,
        showParams: true,
        text: { color: KLINE_TEXT, size: 12, family: 'Helvetica Neue', weight: 'normal', marginLeft: 8, marginTop: 4, marginRight: 8, marginBottom: 4 },
        icons: [
          {
            id: 'toggle_visibility',
            position: 'middle',
            color: KLINE_TEXT_SECONDARY,
            activeColor: KLINE_TEXT,
            size: 14,
            fontFamily: 'Helvetica Neue',
            icon: '👁',
            backgroundColor: 'transparent',
            activeBackgroundColor: 'transparent',
            marginLeft: 8,
            marginTop: 2,
            marginRight: 4,
            marginBottom: 2,
            paddingLeft: 2,
            paddingTop: 2,
            paddingRight: 2,
            paddingBottom: 2
          },
          {
            id: 'settings',
            position: 'middle',
            color: KLINE_TEXT_SECONDARY,
            activeColor: KLINE_TEXT,
            size: 14,
            fontFamily: 'Helvetica Neue',
            icon: '⚙',
            backgroundColor: 'transparent',
            activeBackgroundColor: 'transparent',
            marginLeft: 4,
            marginTop: 2,
            marginRight: 4,
            marginBottom: 2,
            paddingLeft: 2,
            paddingTop: 2,
            paddingRight: 2,
            paddingBottom: 2
          },
          {
            id: 'remove_indicator',
            position: 'middle',
            color: '#F56C6C',
            activeColor: '#F56C6C',
            size: 14,
            fontFamily: 'Helvetica Neue',
            icon: '✖',
            backgroundColor: 'transparent',
            activeBackgroundColor: 'transparent',
            marginLeft: 4,
            marginTop: 2,
            marginRight: 8,
            marginBottom: 2,
            paddingLeft: 2,
            paddingTop: 2,
            paddingRight: 2,
            paddingBottom: 2
          }
        ]
      }
    },
    separator: { color: '#333333' }
  });

  // 应用初始图表类型
  applyChartType(props.chartType);

  // 图表初始化完成后，根据初始 props 创建指标
  console.log('Applying initial indicators:', props.indicators);
  if (props.indicators) {
    ensureIndicator('MA', !!props.indicators.ma);
    ensureIndicator('VOL', !!props.indicators.vol);
    ensureIndicator('MACD', !!props.indicators.macd);
  }

  // 订阅 tooltip 图标点击事件
  chart.subscribeAction('onTooltipIconClick', (payload: any) => {
    try {
      const { paneId, indicatorName, iconId } = payload || {};
      if (!iconId) return;
      // 指标图标
      if (indicatorName && typeof indicatorName === 'string' && indicatorName.length > 0) {
        switch (iconId) {
          case 'toggle_visibility': {
            // 使用正确的API查询当前指标的可见性状态
            const targetIndicator = chart.getIndicatorByPaneId(paneId, indicatorName);
            const currentVisible = targetIndicator?.visible ?? true;
            const next = !currentVisible;
            console.log(`Toggle visibility for ${indicatorName} in pane ${paneId}: ${next}`);
            // 使用 paneId 作用域覆盖指定指标可见性
            chart.overrideIndicator({ name: indicatorName, visible: next }, paneId);
            break;
          }
          case 'remove_indicator': {
            // 检查指标是否已存在
        const existingIndicator = chart.getIndicatorByPaneId(paneId, indicatorName);
        const indicatorExists = !!existingIndicator;
            if (indicatorExists) {
              chart.removeIndicator({ name: indicatorName, paneId });
            }
            break;
          }
          case 'settings': {
            // 向上抛出事件，由父组件弹出参数对话框并通过 overrideIndicator 应用
            emit('open-indicator-settings', { paneId, name: indicatorName });
            break;
          }
          default:
            break;
        }
      } else {
        // 蜡烛图 tooltip 图标（indicatorName 为空字符串），此处仅示例打印
        if (iconId === 'candle_settings') {
          console.log('Candle tooltip settings clicked');
        }
      }
    } catch (e) {
      console.warn('onTooltipIconClick handler error:', e);
    }
  });
  
  // 连接WebSocket
  ws = new WebSocket('ws://localhost:8000/ws');
  
  ws.onopen = () => {
    console.log('Connected to WebSocket server');
  };
  
  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      
      if (message.type === 'bar') {
        const barData = message.data;
        console.log('原始后端数据:', barData);
        
        // 转换数据格式以匹配KLineChart要求
        const klineData = {
          timestamp: new Date(barData.datetime).getTime(),
          open: barData.open_price || barData.open,
          high: barData.high_price || barData.high,
          low: barData.low_price || barData.low,
          close: barData.close_price || barData.close,
          volume: barData.volume
        };
        
        console.log('转换后KLineData:', klineData);
        
        // 若无初始数据，先设置初始数据；否则增量更新
        if (!hasInitialData) {
          chart.applyNewData([klineData]);
          hasInitialData = true;
        } else {
          chart.updateData(klineData);
        }
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
});

// 监听外部传入的图表类型与指标变化
watch(
  () => props.chartType,
  (val) => { applyChartType(val as 'candle' | 'line'); },
  { immediate: false }
);

watch(
  () => props.indicators,
  (val) => {
    console.log('Indicators props changed:', val);
    if (!val || !chart) return;
    ensureIndicator('MA', !!val.ma);
    ensureIndicator('VOL', !!val.vol);
    ensureIndicator('MACD', !!val.macd);
  },
  { deep: true, immediate: false }
);

onUnmounted(() => {
  if (chart) {
    if (chartContainer.value) {
      dispose(chartContainer.value);
    }
  }
  if (ws) {
    ws.close();
  }
});
</script>
