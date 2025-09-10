<template>
  <div ref="chartContainer" class="chart-container"></div>
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
  chart.setStyles({
    grid: {
      horizontal: { color: '#2B2B2B' },
      vertical: { color: '#2B2B2B' }
    },
    xAxis: {
      axisLine: { color: '#555555' },
      tickLine: { color: '#555555' },
      tickText: { color: '#9AA0A6' }
    },
    yAxis: {
      axisLine: { color: '#555555' },
      tickLine: { color: '#555555' },
      tickText: { color: '#9AA0A6' }
    },
    crosshair: {
      horizontal: {
        line: { color: '#666666' },
        text: { backgroundColor: '#333333', borderColor: '#333333', color: '#FFFFFF' }
      },
      vertical: {
        line: { color: '#666666' },
        text: { backgroundColor: '#333333', borderColor: '#333333', color: '#FFFFFF' }
      }
    },
    candle: {
      priceMark: {
        last: {
          line: { show: true, style: 'dashed', dashedValue: [4, 4], size: 1 },
          text: { show: true, style: 'fill', color: '#FFFFFF' }
        }
      }
    },
    tooltip: {
      showRule: 'always',
      showType: 'standard',
      rect: { position: 'fixed', borderColor: '#3C4043', color: '#1E1E1E' },
      title: { color: '#9AA0A6' },
      legend: { color: '#E8EAED' }
    },
    separator: { color: '#444444' }
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
          open: barData.open_price,
          high: barData.high_price,
          low: barData.low_price,
          close: barData.close_price,
          volume: barData.volume
        };
        
        console.log('转换后KLineData:', klineData);
        console.log('timestamp量级:', klineData.timestamp, '是否>1e12:', klineData.timestamp > 1e12);
        
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
    dispose(chartContainer.value);
  }
  if (ws) {
    ws.close();
  }
});
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 600px;
  background-color: #0B1015;
}
</style>
