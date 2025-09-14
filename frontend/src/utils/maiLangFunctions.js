/**
 * 麦语言函数库JavaScript实现
 * 基于MyTT库移植，支持常用技术指标计算
 */

/**
 * 基础工具函数
 */
export class MaiLangFunctions {
  /**
   * 移动平均线 MA
   * @param {Array} data - 数据序列
   * @param {number} period - 周期
   * @returns {Array} MA值序列
   */
  static MA(data, period) {
    if (!Array.isArray(data) || data.length < period) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    
    for (let i = period - 1; i < data.length; i++) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j];
      }
      result[i] = sum / period;
    }
    
    return result;
  }

  /**
   * 指数移动平均线 EMA
   * @param {Array} data - 数据序列
   * @param {number} period - 周期
   * @returns {Array} EMA值序列
   */
  static EMA(data, period) {
    if (!Array.isArray(data) || data.length === 0) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    const multiplier = 2 / (period + 1);
    
    // 第一个EMA值使用SMA
    let sum = 0;
    for (let i = 0; i < Math.min(period, data.length); i++) {
      sum += data[i];
    }
    result[period - 1] = sum / period;
    
    // 后续EMA值
    for (let i = period; i < data.length; i++) {
      result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1];
    }
    
    return result;
  }

  /**
   * 简单移动平均线 SMA (与MA相同)
   */
  static SMA(data, period) {
    return this.MA(data, period);
  }

  /**
   * 加权移动平均线 WMA
   * @param {Array} data - 数据序列
   * @param {number} period - 周期
   * @returns {Array} WMA值序列
   */
  static WMA(data, period) {
    if (!Array.isArray(data) || data.length < period) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    const weightSum = (period * (period + 1)) / 2;
    
    for (let i = period - 1; i < data.length; i++) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j] * (period - j);
      }
      result[i] = sum / weightSum;
    }
    
    return result;
  }

  /**
   * 引用函数 REF
   * @param {Array} data - 数据序列
   * @param {number} period - 引用周期数
   * @returns {Array} 引用后的序列
   */
  static REF(data, period) {
    if (!Array.isArray(data)) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    
    for (let i = period; i < data.length; i++) {
      result[i] = data[i - period];
    }
    
    return result;
  }

  /**
   * 求和函数 SUM
   * @param {Array} data - 数据序列
   * @param {number} period - 求和周期
   * @returns {Array} 求和序列
   */
  static SUM(data, period) {
    if (!Array.isArray(data) || data.length < period) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    
    for (let i = period - 1; i < data.length; i++) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j];
      }
      result[i] = sum;
    }
    
    return result;
  }

  /**
   * 标准差 STD
   * @param {Array} data - 数据序列
   * @param {number} period - 计算周期
   * @returns {Array} 标准差序列
   */
  static STD(data, period) {
    if (!Array.isArray(data) || data.length < period) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    
    for (let i = period - 1; i < data.length; i++) {
      // 计算平均值
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j];
      }
      const mean = sum / period;
      
      // 计算方差
      let variance = 0;
      for (let j = 0; j < period; j++) {
        variance += Math.pow(data[i - j] - mean, 2);
      }
      
      result[i] = Math.sqrt(variance / period);
    }
    
    return result;
  }

  /**
   * 最高值 HHV
   * @param {Array} data - 数据序列
   * @param {number} period - 计算周期
   * @returns {Array} 最高值序列
   */
  static HHV(data, period) {
    if (!Array.isArray(data) || data.length < period) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    
    for (let i = period - 1; i < data.length; i++) {
      let max = data[i - period + 1];
      for (let j = 1; j < period; j++) {
        max = Math.max(max, data[i - j]);
      }
      result[i] = max;
    }
    
    return result;
  }

  /**
   * 最低值 LLV
   * @param {Array} data - 数据序列
   * @param {number} period - 计算周期
   * @returns {Array} 最低值序列
   */
  static LLV(data, period) {
    if (!Array.isArray(data) || data.length < period) {
      return [];
    }
    
    const result = new Array(data.length).fill(null);
    
    for (let i = period - 1; i < data.length; i++) {
      let min = data[i - period + 1];
      for (let j = 1; j < period; j++) {
        min = Math.min(min, data[i - j]);
      }
      result[i] = min;
    }
    
    return result;
  }

  /**
   * 计数函数 COUNT
   * @param {Array} condition - 条件序列
   * @param {number} period - 计算周期
   * @returns {Array} 计数序列
   */
  static COUNT(condition, period) {
    if (!Array.isArray(condition) || condition.length < period) {
      return [];
    }
    
    const result = new Array(condition.length).fill(null);
    
    for (let i = period - 1; i < condition.length; i++) {
      let count = 0;
      for (let j = 0; j < period; j++) {
        if (condition[i - j]) {
          count++;
        }
      }
      result[i] = count;
    }
    
    return result;
  }

  /**
   * 全部满足 EVERY
   * @param {Array} condition - 条件序列
   * @param {number} period - 计算周期
   * @returns {Array} 布尔序列
   */
  static EVERY(condition, period) {
    if (!Array.isArray(condition) || condition.length < period) {
      return [];
    }
    
    const result = new Array(condition.length).fill(null);
    
    for (let i = period - 1; i < condition.length; i++) {
      let allTrue = true;
      for (let j = 0; j < period; j++) {
        if (!condition[i - j]) {
          allTrue = false;
          break;
        }
      }
      result[i] = allTrue;
    }
    
    return result;
  }

  /**
   * 存在满足 EXIST
   * @param {Array} condition - 条件序列
   * @param {number} period - 计算周期
   * @returns {Array} 布尔序列
   */
  static EXIST(condition, period) {
    if (!Array.isArray(condition) || condition.length < period) {
      return [];
    }
    
    const result = new Array(condition.length).fill(null);
    
    for (let i = period - 1; i < condition.length; i++) {
      let exists = false;
      for (let j = 0; j < period; j++) {
        if (condition[i - j]) {
          exists = true;
          break;
        }
      }
      result[i] = exists;
    }
    
    return result;
  }

  /**
   * 交叉函数 CROSS
   * @param {Array} data1 - 数据序列1
   * @param {Array} data2 - 数据序列2
   * @returns {Array} 交叉信号序列
   */
  static CROSS(data1, data2) {
    if (!Array.isArray(data1) || !Array.isArray(data2) || data1.length !== data2.length) {
      return [];
    }
    
    const result = new Array(data1.length).fill(false);
    
    for (let i = 1; i < data1.length; i++) {
      if (data1[i - 1] <= data2[i - 1] && data1[i] > data2[i]) {
        result[i] = true;
      }
    }
    
    return result;
  }

  /**
   * 上次条件成立到现在的周期数 BARSLAST
   * @param {Array} condition - 条件序列
   * @returns {Array} 周期数序列
   */
  static BARSLAST(condition) {
    if (!Array.isArray(condition)) {
      return [];
    }
    
    const result = new Array(condition.length).fill(null);
    let lastTrueIndex = -1;
    
    for (let i = 0; i < condition.length; i++) {
      if (condition[i]) {
        lastTrueIndex = i;
        result[i] = 0;
      } else if (lastTrueIndex >= 0) {
        result[i] = i - lastTrueIndex;
      }
    }
    
    return result;
  }

  /**
   * 条件函数 IF
   * @param {Array} condition - 条件序列
   * @param {Array} trueValue - 条件为真时的值
   * @param {Array} falseValue - 条件为假时的值
   * @returns {Array} 结果序列
   */
  static IF(condition, trueValue, falseValue) {
    if (!Array.isArray(condition)) {
      return [];
    }
    
    const result = new Array(condition.length).fill(null);
    
    for (let i = 0; i < condition.length; i++) {
      if (condition[i]) {
        result[i] = Array.isArray(trueValue) ? trueValue[i] : trueValue;
      } else {
        result[i] = Array.isArray(falseValue) ? falseValue[i] : falseValue;
      }
    }
    
    return result;
  }

  /**
   * MACD指标
   * @param {Array} close - 收盘价序列
   * @param {number} fastPeriod - 快线周期，默认12
   * @param {number} slowPeriod - 慢线周期，默认26
   * @param {number} signalPeriod - 信号线周期，默认9
   * @returns {Object} {DIF, DEA, MACD}
   */
  static MACD(close, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
    const fastEMA = this.EMA(close, fastPeriod);
    const slowEMA = this.EMA(close, slowPeriod);
    
    // 计算DIF
    const DIF = new Array(close.length).fill(null);
    for (let i = 0; i < close.length; i++) {
      if (fastEMA[i] !== null && slowEMA[i] !== null) {
        DIF[i] = fastEMA[i] - slowEMA[i];
      }
    }
    
    // 计算DEA
    const DEA = this.EMA(DIF.filter(v => v !== null), signalPeriod);
    
    // 补齐DEA数组长度
    const fullDEA = new Array(close.length).fill(null);
    let deaIndex = 0;
    for (let i = 0; i < close.length; i++) {
      if (DIF[i] !== null && deaIndex < DEA.length) {
        fullDEA[i] = DEA[deaIndex++];
      }
    }
    
    // 计算MACD柱
    const MACD = new Array(close.length).fill(null);
    for (let i = 0; i < close.length; i++) {
      if (DIF[i] !== null && fullDEA[i] !== null) {
        MACD[i] = (DIF[i] - fullDEA[i]) * 2;
      }
    }
    
    return { DIF, DEA: fullDEA, MACD };
  }

  /**
   * KDJ指标
   * @param {Array} high - 最高价序列
   * @param {Array} low - 最低价序列
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认9
   * @param {number} m1 - K值平滑参数，默认3
   * @param {number} m2 - D值平滑参数，默认3
   * @returns {Object} {K, D, J}
   */
  static KDJ(high, low, close, period = 9, m1 = 3, m2 = 3) {
    const length = close.length;
    const RSV = new Array(length).fill(null);
    const K = new Array(length).fill(50);
    const D = new Array(length).fill(50);
    const J = new Array(length).fill(null);
    
    // 计算RSV
    for (let i = period - 1; i < length; i++) {
      let highestHigh = high[i - period + 1];
      let lowestLow = low[i - period + 1];
      
      for (let j = i - period + 2; j <= i; j++) {
        highestHigh = Math.max(highestHigh, high[j]);
        lowestLow = Math.min(lowestLow, low[j]);
      }
      
      if (highestHigh !== lowestLow) {
        RSV[i] = ((close[i] - lowestLow) / (highestHigh - lowestLow)) * 100;
      } else {
        RSV[i] = 50;
      }
    }
    
    // 计算K、D、J
    for (let i = period - 1; i < length; i++) {
      if (RSV[i] !== null) {
        K[i] = (K[i - 1] * (m1 - 1) + RSV[i]) / m1;
        D[i] = (D[i - 1] * (m2 - 1) + K[i]) / m2;
        J[i] = 3 * K[i] - 2 * D[i];
      }
    }
    
    return { K, D, J };
  }

  /**
   * RSI指标
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认14
   * @returns {Array} RSI值序列
   */
  static RSI(close, period = 14) {
    if (close.length < period + 1) {
      return new Array(close.length).fill(null);
    }
    
    const result = new Array(close.length).fill(null);
    const gains = [];
    const losses = [];
    
    // 计算价格变化
    for (let i = 1; i < close.length; i++) {
      const change = close[i] - close[i - 1];
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? -change : 0);
    }
    
    // 计算初始平均收益和损失
    let avgGain = 0;
    let avgLoss = 0;
    
    for (let i = 0; i < period; i++) {
      avgGain += gains[i];
      avgLoss += losses[i];
    }
    
    avgGain /= period;
    avgLoss /= period;
    
    // 计算RSI
    for (let i = period; i < close.length; i++) {
      if (avgLoss === 0) {
        result[i] = 100;
      } else {
        const rs = avgGain / avgLoss;
        result[i] = 100 - (100 / (1 + rs));
      }
      
      // 更新平均收益和损失（使用Wilder's平滑）
      if (i < gains.length) {
        avgGain = (avgGain * (period - 1) + gains[i]) / period;
        avgLoss = (avgLoss * (period - 1) + losses[i]) / period;
      }
    }
    
    return result;
  }

  /**
   * 布林带指标 BOLL
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认20
   * @param {number} stdDev - 标准差倍数，默认2
   * @returns {Object} {UP, MID, DOWN}
   */
  static BOLL(close, period = 20, stdDev = 2) {
    const MID = this.MA(close, period);
    const std = this.STD(close, period);
    
    const UP = new Array(close.length).fill(null);
    const DOWN = new Array(close.length).fill(null);
    
    for (let i = 0; i < close.length; i++) {
      if (MID[i] !== null && std[i] !== null) {
        UP[i] = MID[i] + stdDev * std[i];
        DOWN[i] = MID[i] - stdDev * std[i];
      }
    }
    
    return { UP, MID, DOWN };
  }

  /**
   * ATR指标（平均真实波幅）
   * @param {Array} high - 最高价序列
   * @param {Array} low - 最低价序列
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认14
   * @returns {Array} ATR值序列
   */
  static ATR(high, low, close, period = 14) {
    const trueRange = new Array(close.length).fill(null);
    
    // 计算真实波幅
    for (let i = 1; i < close.length; i++) {
      const tr1 = high[i] - low[i];
      const tr2 = Math.abs(high[i] - close[i - 1]);
      const tr3 = Math.abs(low[i] - close[i - 1]);
      trueRange[i] = Math.max(tr1, tr2, tr3);
    }
    
    // 计算ATR（使用EMA平滑）
    return this.EMA(trueRange.slice(1), period);
  }

  /**
   * CCI指标（顺势指标）
   * @param {Array} high - 最高价序列
   * @param {Array} low - 最低价序列
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认14
   * @returns {Array} CCI值序列
   */
  static CCI(high, low, close, period = 14) {
    // 计算典型价格
    const tp = [];
    for (let i = 0; i < close.length; i++) {
      tp.push((high[i] + low[i] + close[i]) / 3);
    }
    
    const result = new Array(close.length).fill(null);
    
    for (let i = period - 1; i < close.length; i++) {
      // 计算典型价格的移动平均
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += tp[i - j];
      }
      const smaTP = sum / period;
      
      // 计算平均偏差
      let deviation = 0;
      for (let j = 0; j < period; j++) {
        deviation += Math.abs(tp[i - j] - smaTP);
      }
      const meanDeviation = deviation / period;
      
      // 计算CCI
      if (meanDeviation !== 0) {
        result[i] = (tp[i] - smaTP) / (0.015 * meanDeviation);
      }
    }
    
    return result;
  }

  /**
   * WR指标（威廉指标）
   * @param {Array} high - 最高价序列
   * @param {Array} low - 最低价序列
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认14
   * @returns {Array} WR值序列
   */
  static WR(high, low, close, period = 14) {
    const result = new Array(close.length).fill(null);
    
    for (let i = period - 1; i < close.length; i++) {
      let highestHigh = high[i - period + 1];
      let lowestLow = low[i - period + 1];
      
      for (let j = i - period + 2; j <= i; j++) {
        highestHigh = Math.max(highestHigh, high[j]);
        lowestLow = Math.min(lowestLow, low[j]);
      }
      
      if (highestHigh !== lowestLow) {
        result[i] = ((highestHigh - close[i]) / (highestHigh - lowestLow)) * -100;
      }
    }
    
    return result;
  }

  /**
   * BIAS指标（乖离率）
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认6
   * @returns {Array} BIAS值序列
   */
  static BIAS(close, period = 6) {
    const ma = this.MA(close, period);
    const result = new Array(close.length).fill(null);
    
    for (let i = 0; i < close.length; i++) {
      if (ma[i] !== null && ma[i] !== 0) {
        result[i] = ((close[i] - ma[i]) / ma[i]) * 100;
      }
    }
    
    return result;
  }

  /**
   * PSY指标（心理线）
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认12
   * @returns {Array} PSY值序列
   */
  static PSY(close, period = 12) {
    const result = new Array(close.length).fill(null);
    
    for (let i = period; i < close.length; i++) {
      let upDays = 0;
      for (let j = 1; j <= period; j++) {
        if (close[i - j + 1] > close[i - j]) {
          upDays++;
        }
      }
      result[i] = (upDays / period) * 100;
    }
    
    return result;
  }

  /**
   * DMI指标（趋向指标）
   * @param {Array} high - 最高价序列
   * @param {Array} low - 最低价序列
   * @param {Array} close - 收盘价序列
   * @param {number} period - 计算周期，默认14
   * @returns {Object} {PDI, MDI, ADX, ADXR}
   */
  static DMI(high, low, close, period = 14) {
    const length = close.length;
    const TR = new Array(length).fill(null);
    const PDM = new Array(length).fill(null);
    const MDM = new Array(length).fill(null);
    
    // 计算TR、+DM、-DM
    for (let i = 1; i < length; i++) {
      const hl = high[i] - low[i];
      const hc = Math.abs(high[i] - close[i - 1]);
      const lc = Math.abs(low[i] - close[i - 1]);
      TR[i] = Math.max(hl, hc, lc);
      
      const hh = high[i] - high[i - 1];
      const ll = low[i - 1] - low[i];
      
      PDM[i] = (hh > 0 && hh > ll) ? hh : 0;
      MDM[i] = (ll > 0 && ll > hh) ? ll : 0;
    }
    
    // 计算平滑的TR、+DM、-DM
    const smoothTR = this.EMA(TR.slice(1), period);
    const smoothPDM = this.EMA(PDM.slice(1), period);
    const smoothMDM = this.EMA(MDM.slice(1), period);
    
    // 计算DI
    const PDI = new Array(length).fill(null);
    const MDI = new Array(length).fill(null);
    const DX = new Array(length).fill(null);
    
    for (let i = 0; i < smoothTR.length; i++) {
      if (smoothTR[i] !== null && smoothTR[i] !== 0) {
        PDI[i + period] = (smoothPDM[i] / smoothTR[i]) * 100;
        MDI[i + period] = (smoothMDM[i] / smoothTR[i]) * 100;
        
        const sum = PDI[i + period] + MDI[i + period];
        if (sum !== 0) {
          DX[i + period] = (Math.abs(PDI[i + period] - MDI[i + period]) / sum) * 100;
        }
      }
    }
    
    // 计算ADX
    const ADX = this.EMA(DX.filter(v => v !== null), period);
    
    // 补齐ADX数组
    const fullADX = new Array(length).fill(null);
    let adxIndex = 0;
    for (let i = 0; i < length; i++) {
      if (DX[i] !== null && adxIndex < ADX.length) {
        fullADX[i] = ADX[adxIndex++];
      }
    }
    
    // 计算ADXR
    const ADXR = new Array(length).fill(null);
    for (let i = period; i < length; i++) {
      if (fullADX[i] !== null && fullADX[i - period] !== null) {
        ADXR[i] = (fullADX[i] + fullADX[i - period]) / 2;
      }
    }
    
    return { PDI, MDI, ADX: fullADX, ADXR };
  }
}

// 导出所有函数
export default MaiLangFunctions;