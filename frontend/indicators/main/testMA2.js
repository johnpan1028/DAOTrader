/**
 * testMA2 指标
 * 自动生成于 2025/9/14 21:15:37
 * 原始麦语言代码:
 * // 测试指标 - 简单移动平均线
 * // 这是一个主图指标示例
 * 
 * // 参数定义
 * PERIOD := 20
 * 
 * // 计算移动平均线
 * MA_LINE := MA(CLOSE, PERIOD)
 */

const testMA2 = {
  name: 'testMA2',
  shortName: 'CUSTOM',
  calcParams: [
  {
    "name": "param1",
    "value": 20,
    "type": "number"
  }
],
  figures: [
  {
    "key": "period",
    "title": "PERIOD",
    "type": "line",
    "baseValue": null,
    "styles": {
      "style": "solid",
      "smooth": false,
      "size": 1,
      "color": "#004E89"
    }
  },
  {
    "key": "ma_line",
    "title": "MA_LINE",
    "type": "line",
    "baseValue": null,
    "styles": {
      "style": "solid",
      "smooth": false,
      "size": 1,
      "color": "#FF6B35"
    }
  }
],
  calc: function(dataList, calcParams) {
  const result = [];
  
  for (let i = 0; i < dataList.length; i++) {
    const data = {
      open: dataList[i].open,
      high: dataList[i].high,
      low: dataList[i].low,
      close: dataList[i].close,
      volume: dataList[i].volume
    };
    
    const indicatorData = {};
    
    indicatorData.period = 20;
    indicatorData.ma_line = this.MA(data.close, PERIOD);
    
    result.push(indicatorData);
  }
  
  return result;
},
  regenerateFigures: null,
  createTooltipDataSource: null,
  draw: null
}

export default testMA2
