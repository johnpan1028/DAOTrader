/**
 * 期货数据API服务
 * 提供期货合约、数据获取等相关接口
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * HTTP请求工具函数
 */
class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      return {
        success: true,
        data: data,
        status: response.status
      }
    } catch (error) {
      console.error(`API请求失败 [${endpoint}]:`, error)
      return {
        success: false,
        error: error.message,
        data: null
      }
    }
  }

  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${endpoint}?${queryString}` : endpoint
    return this.request(url, { method: 'GET' })
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' })
  }
}

// 创建API客户端实例
const apiClient = new ApiClient()

/**
 * 期货API服务类
 */
export class FuturesApi {
  /**
   * 获取所有期货合约
   * @returns {Promise<Object>} 合约字典
   */
  static async getContracts() {
    return apiClient.get('/futures/contracts')
  }

  /**
   * 根据交易所获取合约
   * @param {string} exchange - 交易所名称
   * @returns {Promise<Object>} 合约列表
   */
  static async getContractsByExchange(exchange) {
    return apiClient.get('/futures/contracts/by-exchange', { exchange })
  }

  /**
   * 根据分类获取合约
   * @param {string} category - 品种分类
   * @returns {Promise<Object>} 合约列表
   */
  static async getContractsByCategory(category) {
    return apiClient.get('/futures/contracts/by-category', { category })
  }

  /**
   * 搜索合约
   * @param {string} keyword - 搜索关键词
   * @returns {Promise<Object>} 搜索结果
   */
  static async searchContracts(keyword) {
    return apiClient.get('/futures/contracts/search', { keyword })
  }

  /**
   * 获取交易所列表
   * @returns {Promise<Object>} 交易所信息
   */
  static async getExchanges() {
    return apiClient.get('/futures/exchanges')
  }

  /**
   * 获取品种分类列表
   * @returns {Promise<Object>} 分类信息
   */
  static async getCategories() {
    return apiClient.get('/futures/categories')
  }

  /**
   * 获取统计信息
   * @returns {Promise<Object>} 统计数据
   */
  static async getStatistics() {
    return apiClient.get('/futures/statistics')
  }

  /**
   * 获取期货日线数据
   * @param {string} symbol - 合约代码
   * @param {string} startDate - 开始日期 (YYYY-MM-DD)
   * @param {string} endDate - 结束日期 (YYYY-MM-DD)
   * @param {string} period - 数据周期 (daily, weekly, monthly)
   * @returns {Promise<Object>} 历史数据
   */
  static async getDailyData(symbol, startDate = null, endDate = null, period = 'daily') {
    const params = { symbol, period }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    return apiClient.get('/futures/data/daily', params)
  }

  /**
   * 获取期货实时数据
   * @param {string|Array} symbols - 合约代码或代码数组
   * @returns {Promise<Object>} 实时数据
   */
  static async getRealTimeData(symbols) {
    const symbolsParam = Array.isArray(symbols) ? symbols.join(',') : symbols
    return apiClient.get('/futures/data/realtime', { symbols: symbolsParam })
  }

  /**
   * 批量获取期货数据
   * @param {Array} symbols - 合约代码数组
   * @param {string} startDate - 开始日期
   * @param {string} endDate - 结束日期
   * @param {string} period - 数据周期
   * @returns {Promise<Object>} 批量数据
   */
  static async getBatchData(symbols, startDate = null, endDate = null, period = 'daily') {
    const data = {
      symbols,
      period,
      start_date: startDate,
      end_date: endDate
    }
    
    return apiClient.post('/futures/data/batch', data)
  }

  /**
   * 验证合约代码
   * @param {string} symbol - 合约代码
   * @returns {Promise<Object>} 验证结果
   */
  static async validateSymbol(symbol) {
    return apiClient.get('/futures/validate', { symbol })
  }

  /**
   * 获取合约详细信息
   * @param {string} symbol - 合约代码
   * @returns {Promise<Object>} 合约详情
   */
  static async getContractInfo(symbol) {
    return apiClient.get(`/futures/contracts/${symbol}`)
  }

  /**
   * 获取主力合约映射
   * @param {string} underlying - 标的品种
   * @returns {Promise<Object>} 主力合约信息
   */
  static async getMainContract(underlying) {
    return apiClient.get('/futures/main-contract', { underlying })
  }

  /**
   * 获取连续合约数据
   * @param {string} underlying - 标的品种
   * @param {string} startDate - 开始日期
   * @param {string} endDate - 结束日期
   * @returns {Promise<Object>} 连续合约数据
   */
  static async getContinuousData(underlying, startDate = null, endDate = null) {
    const params = { underlying }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    return apiClient.get('/futures/data/continuous', params)
  }

  /**
   * 获取期货基本面数据
   * @param {string} symbol - 合约代码
   * @returns {Promise<Object>} 基本面数据
   */
  static async getFundamentalData(symbol) {
    return apiClient.get('/futures/fundamental', { symbol })
  }

  /**
   * 获取持仓数据
   * @param {string} symbol - 合约代码
   * @param {string} date - 日期
   * @returns {Promise<Object>} 持仓数据
   */
  static async getPositionData(symbol, date = null) {
    const params = { symbol }
    if (date) params.date = date
    
    return apiClient.get('/futures/position', params)
  }

  /**
   * 获取交割信息
   * @param {string} symbol - 合约代码
   * @returns {Promise<Object>} 交割信息
   */
  static async getDeliveryInfo(symbol) {
    return apiClient.get('/futures/delivery', { symbol })
  }
}

/**
 * 数据缓存管理
 */
class DataCache {
  constructor(maxSize = 100, ttl = 5 * 60 * 1000) { // 默认5分钟TTL
    this.cache = new Map()
    this.maxSize = maxSize
    this.ttl = ttl
  }

  set(key, value) {
    // 如果缓存已满，删除最旧的条目
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }

    this.cache.set(key, {
      value,
      timestamp: Date.now()
    })
  }

  get(key) {
    const item = this.cache.get(key)
    if (!item) return null

    // 检查是否过期
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.value
  }

  clear() {
    this.cache.clear()
  }

  has(key) {
    const item = this.cache.get(key)
    if (!item) return false

    // 检查是否过期
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key)
      return false
    }

    return true
  }
}

// 创建缓存实例
const dataCache = new DataCache()

/**
 * 带缓存的期货API服务
 */
export class CachedFuturesApi extends FuturesApi {
  /**
   * 带缓存的获取合约数据
   */
  static async getContracts() {
    const cacheKey = 'futures:contracts'
    const cached = dataCache.get(cacheKey)
    
    if (cached) {
      return { success: true, data: cached, fromCache: true }
    }

    const result = await super.getContracts()
    if (result.success) {
      dataCache.set(cacheKey, result.data)
    }

    return result
  }

  /**
   * 带缓存的获取实时数据
   */
  static async getRealTimeData(symbols) {
    const symbolsKey = Array.isArray(symbols) ? symbols.sort().join(',') : symbols
    const cacheKey = `futures:realtime:${symbolsKey}`
    const cached = dataCache.get(cacheKey)
    
    if (cached) {
      return { success: true, data: cached, fromCache: true }
    }

    const result = await super.getRealTimeData(symbols)
    if (result.success) {
      // 实时数据缓存时间较短
      const shortCache = new DataCache(50, 30 * 1000) // 30秒
      shortCache.set(cacheKey, result.data)
    }

    return result
  }

  /**
   * 清除缓存
   */
  static clearCache() {
    dataCache.clear()
  }
}

/**
 * 数据格式化工具
 */
export class DataFormatter {
  /**
   * 格式化价格数据
   * @param {number} price - 价格
   * @param {number} precision - 精度
   * @returns {string} 格式化后的价格
   */
  static formatPrice(price, precision = 2) {
    if (price === null || price === undefined) return '--'
    return Number(price).toFixed(precision)
  }

  /**
   * 格式化涨跌幅
   * @param {number} change - 涨跌额
   * @param {number} changePercent - 涨跌幅
   * @returns {Object} 格式化结果
   */
  static formatChange(change, changePercent) {
    const formattedChange = this.formatPrice(change)
    const formattedPercent = this.formatPrice(changePercent) + '%'
    
    let className = 'neutral'
    if (change > 0) className = 'positive'
    else if (change < 0) className = 'negative'
    
    return {
      change: formattedChange,
      percent: formattedPercent,
      className,
      isPositive: change > 0,
      isNegative: change < 0
    }
  }

  /**
   * 格式化成交量
   * @param {number} volume - 成交量
   * @returns {string} 格式化后的成交量
   */
  static formatVolume(volume) {
    if (!volume) return '--'
    
    if (volume >= 100000000) {
      return (volume / 100000000).toFixed(2) + '亿'
    } else if (volume >= 10000) {
      return (volume / 10000).toFixed(2) + '万'
    } else {
      return volume.toString()
    }
  }

  /**
   * 格式化日期时间
   * @param {string|Date} datetime - 日期时间
   * @param {string} format - 格式类型
   * @returns {string} 格式化后的日期时间
   */
  static formatDateTime(datetime, format = 'datetime') {
    if (!datetime) return '--'
    
    const date = new Date(datetime)
    if (isNaN(date.getTime())) return '--'
    
    switch (format) {
      case 'date':
        return date.toLocaleDateString('zh-CN')
      case 'time':
        return date.toLocaleTimeString('zh-CN')
      case 'datetime':
        return date.toLocaleString('zh-CN')
      case 'short':
        return `${date.getMonth() + 1}/${date.getDate()}`
      default:
        return date.toLocaleString('zh-CN')
    }
  }
}

/**
 * 错误处理工具
 */
export class ErrorHandler {
  /**
   * 处理API错误
   * @param {Error} error - 错误对象
   * @param {string} context - 错误上下文
   * @returns {Object} 错误信息
   */
  static handleApiError(error, context = '') {
    console.error(`API错误 [${context}]:`, error)
    
    let message = '网络请求失败'
    let code = 'NETWORK_ERROR'
    
    if (error.message.includes('HTTP 404')) {
      message = '请求的资源不存在'
      code = 'NOT_FOUND'
    } else if (error.message.includes('HTTP 500')) {
      message = '服务器内部错误'
      code = 'SERVER_ERROR'
    } else if (error.message.includes('HTTP 403')) {
      message = '访问被拒绝'
      code = 'FORBIDDEN'
    } else if (error.message.includes('Failed to fetch')) {
      message = '网络连接失败，请检查网络设置'
      code = 'CONNECTION_ERROR'
    }
    
    return {
      message,
      code,
      originalError: error
    }
  }

  /**
   * 显示用户友好的错误消息
   * @param {Object} errorInfo - 错误信息
   * @returns {string} 用户友好的错误消息
   */
  static getUserFriendlyMessage(errorInfo) {
    const messages = {
      'NETWORK_ERROR': '网络连接异常，请稍后重试',
      'NOT_FOUND': '请求的数据不存在',
      'SERVER_ERROR': '服务器暂时不可用，请稍后重试',
      'FORBIDDEN': '没有访问权限',
      'CONNECTION_ERROR': '无法连接到服务器，请检查网络连接'
    }
    
    return messages[errorInfo.code] || errorInfo.message || '未知错误'
  }
}

// 导出默认实例
export const futuresApi = FuturesApi
export const cachedFuturesApi = CachedFuturesApi
export const dataFormatter = DataFormatter
export const errorHandler = ErrorHandler

// 导出便捷方法
export default {
  FuturesApi,
  CachedFuturesApi,
  DataFormatter,
  ErrorHandler,
  futuresApi,
  cachedFuturesApi,
  dataFormatter,
  errorHandler
}