/**
 * 自定义指标库入口文件
 * 统一导入和注册所有自定义指标
 */

// 导入主图指标
import CustomMA from './main/custom-ma.js';

// 导入副图指标
import CustomRSI from './sub/custom-rsi.js';

// 主图指标列表
export const mainIndicators = [
  CustomMA
];

// 副图指标列表
export const subIndicators = [
  CustomRSI
];

// 所有自定义指标
export const allCustomIndicators = [
  ...mainIndicators,
  ...subIndicators
];

// 按类型分组的指标
export const indicatorsByType = {
  main: mainIndicators,
  sub: subIndicators
};

// 指标注册函数
export function registerCustomIndicators(klinecharts) {
  console.log('开始注册自定义指标...');
  
  allCustomIndicators.forEach(indicator => {
    try {
      klinecharts.registerIndicator(indicator);
      console.log(`✓ 成功注册指标: ${indicator.name} (${indicator.shortName})`);
    } catch (error) {
      console.error(`✗ 注册指标失败: ${indicator.name}`, error);
    }
  });
  
  console.log(`自定义指标注册完成，共注册 ${allCustomIndicators.length} 个指标`);
}

// 获取指标信息的辅助函数
export function getIndicatorInfo(name) {
  return allCustomIndicators.find(indicator => indicator.name === name);
}

// 获取主图指标列表
export function getMainIndicators() {
  return mainIndicators.map(indicator => ({
    name: indicator.name,
    shortName: indicator.shortName,
    calcParams: indicator.calcParams
  }));
}

// 获取副图指标列表
export function getSubIndicators() {
  return subIndicators.map(indicator => ({
    name: indicator.name,
    shortName: indicator.shortName,
    calcParams: indicator.calcParams
  }));
}

// 默认导出
export default {
  mainIndicators,
  subIndicators,
  allCustomIndicators,
  indicatorsByType,
  registerCustomIndicators,
  getIndicatorInfo,
  getMainIndicators,
  getSubIndicators
};