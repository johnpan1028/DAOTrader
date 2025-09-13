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
    
    let avgGain = 0;
    let avgLoss = 0;
    
    for (let i = 0; i < dataList.length; i++) {
      const rsiData = {
        overbought: 70,  // 超买线
        oversold: 30     // 超卖线
      };
      
      if (i === 0) {
        result.push(rsiData);
        continue;
      }
      
      const change = dataList[i].close - dataList[i - 1].close;
      const gain = change > 0 ? change : 0;
      const loss = change < 0 ? -change : 0;
      
      if (i < period) {
        // 初始平均值计算
        avgGain = (avgGain * (i - 1) + gain) / i;
        avgLoss = (avgLoss * (i - 1) + loss) / i;
      } else if (i === period) {
        // 第一个RSI值
        avgGain = (avgGain * (period - 1) + gain) / period;
        avgLoss = (avgLoss * (period - 1) + loss) / period;
        
        if (avgLoss === 0) {
          rsiData.rsi = 100;
        } else {
          const rs = avgGain / avgLoss;
          rsiData.rsi = 100 - (100 / (1 + rs));
        }
      } else {
        // 后续RSI值使用平滑移动平均
        avgGain = (avgGain * (period - 1) + gain) / period;
        avgLoss = (avgLoss * (period - 1) + loss) / period;
        
        if (avgLoss === 0) {
          rsiData.rsi = 100;
        } else {
          const rs = avgGain / avgLoss;
          rsiData.rsi = 100 - (100 / (1 + rs));
        }
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