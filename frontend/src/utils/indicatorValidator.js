/**
 * 指标验证器
 * 用于验证编译后的指标是否符合VNPY和KLineChart的格式要求
 */

class IndicatorValidator {
  /**
   * 验证VNPY指标格式
   * @param {Object} vnpyIndicator - VNPY指标对象
   * @returns {Object} 验证结果
   */
  static validateVNPYIndicator(vnpyIndicator) {
    const errors = []
    const warnings = []
    
    // 检查必需字段
    if (!vnpyIndicator.name) {
      errors.push('缺少指标名称 (name)')
    }
    
    if (!vnpyIndicator.calculate) {
      errors.push('缺少计算函数 (calculate)')
    } else if (typeof vnpyIndicator.calculate !== 'function') {
      errors.push('calculate必须是一个函数')
    }
    
    // 检查参数格式
    if (vnpyIndicator.parameters) {
      if (!Array.isArray(vnpyIndicator.parameters)) {
        errors.push('parameters必须是数组格式')
      } else {
        vnpyIndicator.parameters.forEach((param, index) => {
          if (!param.name) {
            errors.push(`参数${index + 1}缺少name字段`)
          }
          if (param.default === undefined) {
            warnings.push(`参数${param.name || index + 1}缺少默认值`)
          }
          if (!param.type) {
            warnings.push(`参数${param.name || index + 1}缺少类型定义`)
          }
        })
      }
    }
    
    // 检查输出格式
    if (vnpyIndicator.outputs) {
      if (!Array.isArray(vnpyIndicator.outputs)) {
        errors.push('outputs必须是数组格式')
      } else {
        vnpyIndicator.outputs.forEach((output, index) => {
          if (!output.name) {
            errors.push(`输出${index + 1}缺少name字段`)
          }
        })
      }
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    }
  }
  
  /**
   * 验证KLineChart指标格式
   * @param {Object} klineIndicator - KLineChart指标对象
   * @returns {Object} 验证结果
   */
  static validateKLineIndicator(klineIndicator) {
    const errors = []
    const warnings = []
    
    // 检查必需字段
    if (!klineIndicator.name) {
      errors.push('缺少指标名称 (name)')
    }
    
    if (!klineIndicator.shortName) {
      warnings.push('建议提供指标简称 (shortName)')
    }
    
    if (!klineIndicator.calc) {
      errors.push('缺少计算函数 (calc)')
    } else if (typeof klineIndicator.calc !== 'function') {
      errors.push('calc必须是一个函数')
    }
    
    // 检查精度设置
    if (klineIndicator.precision !== undefined) {
      if (!Number.isInteger(klineIndicator.precision) || klineIndicator.precision < 0) {
        errors.push('precision必须是非负整数')
      }
    }
    
    // 检查参数格式
    if (klineIndicator.params) {
      if (!Array.isArray(klineIndicator.params)) {
        errors.push('params必须是数组格式')
      } else {
        klineIndicator.params.forEach((param, index) => {
          if (!param.name) {
            errors.push(`参数${index + 1}缺少name字段`)
          }
          if (param.default === undefined) {
            warnings.push(`参数${param.name || index + 1}缺少默认值`)
          }
        })
      }
    }
    
    // 检查绘图配置
    if (klineIndicator.plots) {
      if (!Array.isArray(klineIndicator.plots)) {
        errors.push('plots必须是数组格式')
      } else {
        klineIndicator.plots.forEach((plot, index) => {
          if (!plot.key) {
            errors.push(`绘图配置${index + 1}缺少key字段`)
          }
          if (!plot.title) {
            warnings.push(`绘图配置${plot.key || index + 1}建议提供title`)
          }
          if (!plot.type) {
            warnings.push(`绘图配置${plot.key || index + 1}建议指定type`)
          }
          if (!plot.color) {
            warnings.push(`绘图配置${plot.key || index + 1}建议指定color`)
          }
        })
      }
    } else {
      warnings.push('建议提供plots绘图配置')
    }
    
    // 检查样式生成函数
    if (klineIndicator.styles && typeof klineIndicator.styles !== 'function') {
      errors.push('styles必须是一个函数')
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    }
  }
  
  /**
   * 验证指标计算结果
   * @param {Array} data - K线数据
   * @param {Object} indicator - 指标对象
   * @param {Array} result - 计算结果
   * @returns {Object} 验证结果
   */
  static validateCalculationResult(data, indicator, result) {
    const errors = []
    const warnings = []
    
    if (!Array.isArray(result)) {
      errors.push('指标计算结果必须是数组')
      return { valid: false, errors, warnings }
    }
    
    // 检查结果长度
    if (result.length !== data.length) {
      warnings.push(`计算结果长度(${result.length})与数据长度(${data.length})不匹配`)
    }
    
    // 检查结果格式
    if (result.length > 0) {
      const firstResult = result[0]
      
      if (typeof firstResult === 'object' && firstResult !== null) {
        // 对象格式结果
        const keys = Object.keys(firstResult)
        
        if (indicator.plots) {
          const plotKeys = indicator.plots.map(plot => plot.key)
          const missingKeys = plotKeys.filter(key => !keys.includes(key))
          const extraKeys = keys.filter(key => !plotKeys.includes(key))
          
          if (missingKeys.length > 0) {
            errors.push(`计算结果缺少字段: ${missingKeys.join(', ')}`)
          }
          
          if (extraKeys.length > 0) {
            warnings.push(`计算结果包含额外字段: ${extraKeys.join(', ')}`)
          }
        }
        
        // 检查数值类型
        result.forEach((item, index) => {
          if (typeof item === 'object' && item !== null) {
            Object.entries(item).forEach(([key, value]) => {
              if (value !== null && value !== undefined && typeof value !== 'number') {
                warnings.push(`第${index + 1}项的${key}字段不是数值类型`)
              }
            })
          }
        })
      } else if (typeof firstResult === 'number') {
        // 数值格式结果
        result.forEach((value, index) => {
          if (value !== null && value !== undefined && typeof value !== 'number') {
            warnings.push(`第${index + 1}项不是数值类型`)
          }
        })
      }
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    }
  }
  
  /**
   * 测试指标计算
   * @param {Object} indicator - 指标对象
   * @param {Array} testData - 测试数据
   * @returns {Object} 测试结果
   */
  static testIndicatorCalculation(indicator, testData) {
    const errors = []
    const warnings = []
    let result = null
    
    try {
      // 测试KLineChart格式指标
      if (indicator.calc) {
        const params = indicator.params ? indicator.params.map(p => p.default) : []
        result = indicator.calc(testData, ...params)
        
        // 验证计算结果
        const validation = this.validateCalculationResult(testData, indicator, result)
        errors.push(...validation.errors)
        warnings.push(...validation.warnings)
      }
      
      // 测试VNPY格式指标
      if (indicator.calculate) {
        const vnpyResult = indicator.calculate(testData)
        
        if (vnpyResult && Array.isArray(vnpyResult)) {
          const validation = this.validateCalculationResult(testData, indicator, vnpyResult)
          errors.push(...validation.errors)
          warnings.push(...validation.warnings)
        }
      }
      
    } catch (error) {
      errors.push(`计算过程中发生错误: ${error.message}`)
    }
    
    return {
      success: errors.length === 0,
      result,
      errors,
      warnings
    }
  }
  
  /**
   * 生成测试数据
   * @param {number} count - 数据条数
   * @returns {Array} 测试K线数据
   */
  static generateTestData(count = 100) {
    const data = []
    let basePrice = 100
    let timestamp = Date.now() - count * 24 * 60 * 60 * 1000
    
    for (let i = 0; i < count; i++) {
      const change = (Math.random() - 0.5) * 4
      const open = basePrice
      const close = open + change
      const high = Math.max(open, close) + Math.random() * 2
      const low = Math.min(open, close) - Math.random() * 2
      const volume = Math.floor(Math.random() * 1000000) + 100000
      
      data.push({
        timestamp: timestamp + i * 24 * 60 * 60 * 1000,
        open: Number(open.toFixed(2)),
        high: Number(high.toFixed(2)),
        low: Number(low.toFixed(2)),
        close: Number(close.toFixed(2)),
        volume
      })
      
      basePrice = close
    }
    
    return data
  }
  
  /**
   * 完整验证指标
   * @param {Object} compiledResult - 编译结果
   * @returns {Object} 完整验证结果
   */
  static validateIndicator(compiledResult) {
    const result = {
      valid: true,
      errors: [],
      warnings: [],
      vnpyValidation: null,
      klineValidation: null,
      calculationTest: null
    }
    
    // 验证VNPY格式
    if (compiledResult.vnpyIndicator) {
      result.vnpyValidation = this.validateVNPYIndicator(compiledResult.vnpyIndicator)
      result.errors.push(...result.vnpyValidation.errors)
      result.warnings.push(...result.vnpyValidation.warnings)
    }
    
    // 验证KLineChart格式
    if (compiledResult.klineIndicator) {
      result.klineValidation = this.validateKLineIndicator(compiledResult.klineIndicator)
      result.errors.push(...result.klineValidation.errors)
      result.warnings.push(...result.klineValidation.warnings)
      
      // 测试计算
      const testData = this.generateTestData(50)
      result.calculationTest = this.testIndicatorCalculation(compiledResult.klineIndicator, testData)
      result.errors.push(...result.calculationTest.errors)
      result.warnings.push(...result.calculationTest.warnings)
    }
    
    result.valid = result.errors.length === 0
    
    return result
  }
}

export default IndicatorValidator