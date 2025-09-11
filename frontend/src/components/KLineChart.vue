<template>
  <div class="trading-dashboard">
    <!-- 数据下载控制面板 -->
    <div class="control-panel">
      <h3>数据下载</h3>
      <div class="form-group">
        <label>数据类型:</label>
        <select v-model="dataType">
          <option value="stock">股票</option>
          <option value="futures">期货</option>
        </select>
      </div>
      <div class="form-group">
        <label>合约代码:</label>
        <input v-model="symbol" placeholder="如: 000001 或 RB2509" />
      </div>
      <div class="form-group" v-if="dataType === 'stock'">
        <label>交易所:</label>
        <select v-model="exchange">
          <option value="SSE">上交所</option>
          <option value="SZSE">深交所</option>
        </select>
      </div>
      <div class="form-group" v-if="dataType === 'stock'">
        <label>周期:</label>
        <select v-model="period">
          <option value="daily">日线</option>
          <option value="weekly">周线</option>
          <option value="monthly">月线</option>
        </select>
      </div>
      <div class="form-group">
        <label>开始日期:</label>
        <input type="date" v-model="startDate" />
      </div>
      <div class="form-group">
        <label>结束日期:</label>
        <input type="date" v-model="endDate" />
      </div>
      <button @click="downloadData" :disabled="loading" class="download-btn">
        {{ loading ? '下载中...' : '下载数据' }}
      </button>
      <button @click="loadHistoricalData" :disabled="loading" class="load-btn">
        {{ loading ? '加载中...' : '加载历史数据' }}
      </button>
      <button @click="switchToRealTime" :disabled="loading" class="realtime-btn" v-if="isHistoricalMode">
        切换到实时数据
      </button>
    </div>
    
    <!-- 状态显示 -->
    <div class="status-panel" v-if="message">
      <div :class="['message', messageType]">
        {{ message }}
      </div>
    </div>
    
    <!-- K线图表 -->
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { init, dispose } from 'klinecharts';

const chartContainer = ref<HTMLElement | null>(null);
let chart: any = null;
let ws: WebSocket | null = null;
let hasInitialData = false;
let isHistoricalMode = false; // 标记是否为历史数据模式

// 表单数据
const dataType = ref('futures');
const symbol = ref('RB2509');
const exchange = ref('SSE');
const period = ref('daily');
const startDate = ref('2024-01-01');
const endDate = ref('2024-12-31');
const loading = ref(false);
const message = ref('');
const messageType = ref('info');

// 显示消息
const showMessage = (msg: string, type: 'success' | 'error' | 'info' = 'info') => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 5000);
};

// 下载数据
const downloadData = async () => {
  if (!symbol.value.trim()) {
    showMessage('请输入合约代码', 'error');
    return;
  }
  
  loading.value = true;
  try {
    const endpoint = dataType.value === 'futures' ? '/api/data/download/futures' : '/api/data/download';
    const requestData: any = {
      symbol: symbol.value.trim(),
      start_date: startDate.value,
      end_date: endDate.value
    };
    
    if (dataType.value === 'stock') {
      requestData.exchange = exchange.value;
      requestData.period = period.value;
    }
    
    const response = await fetch(`http://localhost:8000${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    const result = await response.json();
    
    if (result.success) {
      showMessage(result.message, 'success');
    } else {
      showMessage(result.message, 'error');
    }
  } catch (error) {
    showMessage(`下载失败: ${error}`, 'error');
  } finally {
    loading.value = false;
  }
};

// 切换到实时数据模式
const switchToRealTime = () => {
  isHistoricalMode = false;
  hasInitialData = false;
  
  // 重新连接WebSocket
  if (!ws || ws.readyState === WebSocket.CLOSED) {
    ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('重新连接到WebSocket服务器');
      showMessage('已切换到实时数据模式', 'success');
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        
        if (message.type === 'bar') {
          // 如果处于历史数据模式，忽略实时数据
          if (isHistoricalMode) {
            console.log('历史数据模式：忽略实时数据更新');
            return;
          }
          
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
  }
};

// 加载历史数据
const loadHistoricalData = async () => {
  if (!symbol.value.trim()) {
    showMessage('请输入合约代码', 'error');
    return;
  }
  
  loading.value = true;
  try {
    const exchangeParam = dataType.value === 'futures' ? 'SHFE' : exchange.value;
    const intervalParam = dataType.value === 'futures' ? '1d' : '1d';
    
    const response = await fetch(
      `http://localhost:8000/api/data/query?symbol=${symbol.value.trim()}&exchange=${exchangeParam}&interval=${intervalParam}&start=${startDate.value}&end=${endDate.value}&limit=1000`
    );
    
    const result = await response.json();
    
    if (result.success && result.data.length > 0) {
      // 转换数据格式
      const klineData = result.data.map((item: any) => ({
        timestamp: new Date(item.datetime).getTime(),
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }));
      
      console.log('历史数据加载:', klineData.length, '条记录');
      console.log('数据样本:', klineData[0]);
      
      // 切换到历史数据模式
      isHistoricalMode = true;
      
      // 停止WebSocket以避免干扰历史数据显示
      if (ws) {
        ws.close();
        ws = null;
      }
      
      // 应用到图表
      chart.applyNewData(klineData);
      hasInitialData = true;
      showMessage(`成功加载 ${result.data.length} 条历史数据，已切换到历史数据模式`, 'success');
    } else {
      showMessage(result.message || '未找到历史数据', 'error');
    }
  } catch (error) {
    showMessage(`加载失败: ${error}`, 'error');
  } finally {
    loading.value = false;
  }
};

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
        // 如果处于历史数据模式，忽略实时数据
        if (isHistoricalMode) {
          console.log('历史数据模式：忽略实时数据更新');
          return;
        }
        
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
.trading-dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background-color: #1a1a1a;
  color: #ffffff;
}

.control-panel {
  background-color: #2a2a2a;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #444;
}

.control-panel h3 {
  margin: 0 0 20px 0;
  color: #ffffff;
  font-size: 18px;
}

.form-group {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  gap: 10px;
}

.form-group label {
  min-width: 80px;
  color: #cccccc;
  font-size: 14px;
}

.form-group input,
.form-group select {
  padding: 8px 12px;
  border: 1px solid #555;
  border-radius: 4px;
  background-color: #333;
  color: #ffffff;
  font-size: 14px;
  min-width: 150px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
}

.download-btn,
.load-btn {
  padding: 10px 20px;
  margin-right: 10px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.download-btn {
  background-color: #007acc;
  color: white;
}

.download-btn:hover:not(:disabled) {
  background-color: #005a9e;
}

.load-btn {
  background-color: #28a745;
  color: white;
}

.load-btn:hover:not(:disabled) {
  background-color: #1e7e34;
}

.realtime-btn {
  background-color: #17a2b8;
  color: white;
}

.realtime-btn:hover:not(:disabled) {
  background-color: #138496;
}

.download-btn:disabled,
.load-btn:disabled {
  background-color: #666;
  cursor: not-allowed;
}

.status-panel {
  margin-bottom: 10px;
}

.message {
  padding: 12px 16px;
  border-radius: 4px;
  font-size: 14px;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.message.info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.chart-container {
  width: 100%;
  height: 600px;
  background-color: #0B1015;
  border-radius: 8px;
  border: 1px solid #444;
}
</style>
