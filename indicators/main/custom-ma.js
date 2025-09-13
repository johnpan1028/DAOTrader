/**
 * 自定义移动平均线指标 (Custom Moving Average)
 * 主图指标 - 显示在K线图上
 */
export default {
  name: 'CUSTOM_MA',
  shortName: '自定义MA',
  precision: 2,
  calcParams: [5, 10, 20],  // 默认计算5日、10日、20日均线
  series: 'normal',  // 主图指标
  figures: [
    {
      key: 'ma5',
      title: 'MA5: ',
      type: 'line'
    },
    {
      key: 'ma10', 
      title: 'MA10: ',
      type: 'line'
    },
    {
      key: 'ma20',
      title: 'MA20: ',
      type: 'line'
    }
  ],
  
  // 当计算参数改变时重新生成图形配置
  regenerateFigures: (calcParams) => {
    return calcParams.map((param, index) => ({
      key: `ma${index + 1}`,
      title: `MA${param}: `,
      type: 'line'
    }));
  },
  
  // 计算移动平均线
  calc: (dataList, { calcParams }) => {
    return dataList.map((kLineData, i) => {
      const ma = {};
      
      calcParams.forEach((param, j) => {
        if (i >= param - 1) {
          // 计算指定周期的移动平均线
          let sum = 0;
          for (let k = i - param + 1; k <= i; k++) {
            sum += dataList[k].close;
          }
          // 使用与figures中定义一致的键名
          const keys = ['ma5', 'ma10', 'ma20'];
          if (keys[j]) {
            ma[keys[j]] = sum / param;
          }
        }
      });
      
      return ma;
    });
  },
  
  // 自定义样式
  styles: {
    ma5: {
      color: '#FF6B6B'  // 红色
    },
    ma10: {
      color: '#4ECDC4'  // 青色
    },
    ma20: {
      color: '#45B7D1'  // 蓝色
    }
  }
};