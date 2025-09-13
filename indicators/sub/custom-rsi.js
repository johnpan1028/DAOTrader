/**
 * 自定义相对强弱指标 (Custom Relative Strength Index)
 * 副图指标 - 显示在独立面板中
 */
export default {
  name: 'CUSTOM_RSI',
  shortName: '自定义RSI',
  precision: 2,
  calcParams: [14],  // 默认14周期
  series: 'normal',  // 副图指标
  minValue: 0,       // RSI范围0-100
  maxValue: 100,
  figures: [
    {
      key: 'rsi',
      title: 'RSI: ',
      type: 'line'
    },
    {
      key: 'overbought',
      title: '超买线: ',
      type: 'line',
      baseValue: 70
    },
    {
      key: 'oversold',
      title: '超卖线: ',
      type: 'line', 
      baseValue: 30
    }
  ],
  
  // 当计算参数改变时重新生成图形配置
  regenerateFigures: (calcParams) => {
    const period = calcParams[0] || 14;
    return [
      {
        key: 'rsi',
        title: `RSI(${period}): `,
        type: 'line'
      },
      {
        key: 'overbought',
        title: '超买线: ',
        type: 'line'
      },
      {
        key: 'oversold',
        title: '超卖线: ',
        type: 'line'
      }
    ];
  },
  
  // 计算RSI指标
  calc: (dataList, { calcParams }) => {
    const period = calcParams[0] || 14;
    const result = [];
    
    for (let i = 0; i < dataList.length; i++) {
      const rsiData = {
        rsi: null,       // RSI值
        overbought: 70,  // 超买线
        oversold: 30     // 超卖线
      };
      
      if (i < period) {
        // 数据不足，不计算RSI
        result.push(rsiData);
        continue;
      }
      
      // 计算最近period期间的平均收益和损失
      let totalGain = 0;
      let totalLoss = 0;
      
      for (let j = i - period + 1; j <= i; j++) {
        const change = dataList[j].close - dataList[j - 1].close;
        if (change > 0) {
          totalGain += change;
        } else {
          totalLoss += Math.abs(change);
        }
      }
      
      const avgGain = totalGain / period;
      const avgLoss = totalLoss / period;
      
      if (avgLoss === 0) {
        rsiData.rsi = 100;
      } else {
        const rs = avgGain / avgLoss;
        rsiData.rsi = 100 - (100 / (1 + rs));
      }
      
      result.push(rsiData);
    }
    
    return result;
  },
  
  // 自定义样式
  styles: {
    rsi: {
      color: '#FF6B6B',  // 红色RSI线
      size: 2
    },
    overbought: {
      color: '#FFA500',  // 橙色超买线
      size: 1,
      style: 'dashed'
    },
    oversold: {
      color: '#32CD32',  // 绿色超卖线
      size: 1,
      style: 'dashed'
    }
  }
};