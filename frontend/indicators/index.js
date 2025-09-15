// 指标注册文件
// 此文件由系统自动生成和维护

// 主图指标
import * as mainIndicators from './main/index.js';

// 副图指标  
import * as subIndicators from './sub/index.js';

// 导出所有指标
export const indicators = {
  main: mainIndicators,
  sub: subIndicators
};

// 获取所有指标列表
export function getAllIndicators() {
  return {
    main: Object.keys(mainIndicators),
    sub: Object.keys(subIndicators)
  };
}

// 根据名称获取指标
export function getIndicator(name, category = 'sub') {
  if (category === 'main') {
    return mainIndicators[name];
  }
  return subIndicators[name];
}

export default indicators;