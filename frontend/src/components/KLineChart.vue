<template>
  <el-container :style="{ width: '100%', height: '100%' }">
    <el-main :style="{ padding: '0', width: '100%', height: '100%' }">
      <div ref="chartContainer" :style="{ width: '100%', height: '100%', backgroundColor: 'var(--tv-bg-primary)', border: '1px solid var(--tv-border-primary)', borderRadius: '4px', minHeight: '400px' }"></div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { init, dispose } from 'klinecharts';

const chartContainer = ref<HTMLElement | null>(null);
let chart: any = null;
let ws: WebSocket | null = null;
let hasInitialData = false;


onMounted(() => {
  if (!chartContainer.value) return;
  
  // 初始化图表
  chart = init(chartContainer.value);
  // 获取CSS变量值
  const rootStyles = getComputedStyle(document.documentElement);
  const borderColor = rootStyles.getPropertyValue('--el-border-color').trim() || '#2a2e39';
  const textSecondary = rootStyles.getPropertyValue('--el-text-color-secondary').trim() || '#5d606b';
  const textRegular = rootStyles.getPropertyValue('--el-text-color-regular').trim() || '#868993';
  const textPrimary = rootStyles.getPropertyValue('--el-text-color-primary').trim() || '#d1d4dc';
  const bgOverlay = rootStyles.getPropertyValue('--el-bg-color-overlay').trim() || '#1e222d';
  const borderLight = rootStyles.getPropertyValue('--el-border-color-light').trim() || '#434651';
  
  chart.setStyles({
    grid: {
      horizontal: { color: borderColor },
      vertical: { color: borderColor }
    },
    xAxis: {
      axisLine: { color: borderLight },
      tickLine: { color: borderLight },
      tickText: { color: textRegular }
    },
    yAxis: {
      axisLine: { color: borderLight },
      tickLine: { color: borderLight },
      tickText: { color: textRegular }
    },
    crosshair: {
      horizontal: {
        line: { color: textSecondary },
        text: { backgroundColor: bgOverlay, borderColor: bgOverlay, color: textPrimary }
      },
      vertical: {
        line: { color: textSecondary },
        text: { backgroundColor: bgOverlay, borderColor: bgOverlay, color: textPrimary }
      }
    },
    candle: {
      priceMark: {
        last: {
          line: { show: true, style: 'dashed', dashedValue: [4, 4], size: 1 },
          text: { show: true, style: 'fill', color: textPrimary }
        }
      }
    },
    tooltip: {
      showRule: 'always',
      showType: 'standard',
      rect: { position: 'fixed', borderColor: borderLight, color: bgOverlay },
      title: { color: textRegular },
      legend: { color: textPrimary }
    },
    separator: { color: borderColor }
  });
  chart.createIndicator('MA', true, { id: 'candle_pane' });
  chart.createIndicator('VOL', false);
  chart.createIndicator('MACD', false);
  
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
