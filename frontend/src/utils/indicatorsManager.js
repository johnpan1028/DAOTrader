/**
 * Indicators文件夹管理器
 * 负责自动保存编译结果到indicators文件夹
 */

import { maiLangCompiler } from './maiLangCompiler.js';
import { ElMessage } from 'element-plus'

class IndicatorsManager {
  constructor() {
    this.indicatorsPath = './indicators'
    this.watchedFiles = new Map() // 监听的文件映射
  }

  /**
   * 编译并保存指标到indicators文件夹
   * @param {string} maiLangCode - 麦语言代码
   * @param {string} indicatorName - 指标名称
   * @param {string} category - 指标分类 (main/sub)
   * @returns {Promise<object>} 编译和保存结果
   */
  async compileAndSave(maiLangCode, indicatorName, category = 'main') {
    try {
      // 编译麦语言代码
      const compileResult = maiLangCompiler.compile(maiLangCode)
      
      if (!compileResult.success) {
        return {
          success: false,
          error: compileResult.error,
          message: '编译失败'
        }
      }

      // 生成indicators格式的文件内容
      const indicatorContent = this.generateIndicatorFile(
        compileResult.indicatorsFormat,
        indicatorName,
        maiLangCode
      )

      // 保存到indicators文件夹
      const saveResult = await this.saveIndicatorFile(
        indicatorName,
        category,
        indicatorContent
      )

      if (saveResult.success) {
        // 更新index.js注册文件
        await this.updateIndexFile(indicatorName, category)
        
        return {
          success: true,
          message: `指标 ${indicatorName} 已成功保存到indicators文件夹`,
          filePath: saveResult.filePath,
          compileResult
        }
      } else {
        return saveResult
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
        message: '保存过程中发生错误'
      }
    }
  }

  /**
   * 生成indicators格式的文件内容
   */
  generateIndicatorFile(indicatorsFormat, indicatorName, originalCode) {
    const cleanName = this.sanitizeFileName(indicatorName)
    
    return `/**
 * ${indicatorName} 指标
 * 自动生成于 ${new Date().toLocaleString()}
 * 原始麦语言代码:
${originalCode.split('\n').map(line => ` * ${line}`).join('\n')}
 */

const ${cleanName} = {
  name: '${indicatorName}',
  shortName: '${indicatorsFormat.shortName}',
  calcParams: ${JSON.stringify(indicatorsFormat.calcParams, null, 2)},
  figures: ${JSON.stringify(indicatorsFormat.figures, null, 2)},
  calc: ${indicatorsFormat.calc},
  regenerateFigures: null,
  createTooltipDataSource: null,
  draw: null
}

export default ${cleanName}
`
  }

  /**
   * 保存指标文件
   */
  async saveIndicatorFile(indicatorName, category, content) {
    try {
      const cleanName = this.sanitizeFileName(indicatorName)
      const fileName = `${cleanName}.js`
      const filePath = `${this.indicatorsPath}\\${category}\\${fileName}`
      
      // 使用Node.js fs模块写入文件
      const fs = require('fs')
      const path = require('path')
      
      // 确保目录存在
      const dir = path.dirname(filePath)
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true })
      }
      
      // 写入文件
      fs.writeFileSync(filePath, content, 'utf8')
      
      console.log('指标文件已保存:', filePath)
      
      return {
        success: true,
        filePath,
        message: '文件保存成功'
      }
    } catch (error) {
      console.error('保存文件失败:', error)
      return {
        success: false,
        error: error.message,
        message: '文件保存失败'
      }
    }
  }

  /**
   * 更新index.js注册文件
   */
  async updateIndexFile(indicatorName, category) {
    try {
      const cleanName = this.sanitizeFileName(indicatorName)
      const indexPath = `${this.indicatorsPath}\\${category}\\index.js`
      
      const fs = require('fs')
      
      // 读取现有的index.js文件
      let content = fs.readFileSync(indexPath, 'utf8')
      
      // 添加导入语句
      const importStatement = `import ${cleanName} from './${cleanName}.js';`
      const importRegex = /(\/\/ 在这里导入所有.*指标[\s\S]*?)(\/\/ import.*\n)?/
      if (importRegex.test(content)) {
        content = content.replace(importRegex, `$1${importStatement}\n$2`)
      }
      
      // 添加导出语句
      const exportRegex = /(export \{[\s\S]*?)(\s*\/\/ .*\n)?(\s*\};)/
      if (exportRegex.test(content)) {
        content = content.replace(exportRegex, `$1  ${cleanName},\n$2$3`)
      }
      
      // 写入更新后的内容
      fs.writeFileSync(indexPath, content, 'utf8')
      
      console.log('index.js文件已更新:', indexPath)
      
      return {
        success: true,
        message: 'index.js更新成功'
      }
    } catch (error) {
      console.error('更新index.js失败:', error)
      return {
        success: false,
        error: error.message,
        message: 'index.js更新失败'
      }
    }
  }

  /**
   * 清理文件名，移除特殊字符
   */
  sanitizeFileName(name) {
    return name
      .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_') // 替换特殊字符为下划线
      .replace(/^\d/, '_$&') // 如果以数字开头，添加下划线前缀
      .replace(/_{2,}/g, '_') // 合并多个下划线
      .replace(/^_|_$/g, '') // 移除首尾下划线
  }

  /**
   * 监听文件变化并自动重新编译
   */
  watchFile(filePath, maiLangCode, indicatorName, category) {
    // 这里应该实现文件监听逻辑
    // 当文件发生变化时，自动重新编译和保存
    console.log(`开始监听文件: ${filePath}`)
    
    this.watchedFiles.set(filePath, {
      maiLangCode,
      indicatorName,
      category,
      lastModified: Date.now()
    })
  }

  /**
   * 停止监听文件
   */
  unwatchFile(filePath) {
    this.watchedFiles.delete(filePath)
    console.log(`停止监听文件: ${filePath}`)
  }

  /**
   * 获取indicators文件夹中的所有指标
   */
  async getIndicatorsList() {
    try {
      // 这里应该调用后端API获取indicators文件夹中的文件列表
      // 暂时返回模拟数据
      return {
        success: true,
        indicators: {
          main: ['custom-ma.js'],
          sub: ['custom-rsi.js']
        }
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
        message: '获取指标列表失败'
      }
    }
  }

  /**
   * 删除指标文件
   */
  async deleteIndicator(indicatorName, category) {
    try {
      const cleanName = this.sanitizeFileName(indicatorName)
      const filePath = `${this.indicatorsPath}\\${category}\\${cleanName}.js`
      
      // 这里应该调用后端API删除文件
      console.log('删除指标文件:', filePath)
      
      // 同时从index.js中移除注册
      await this.removeFromIndexFile(cleanName, category)
      
      return {
        success: true,
        message: `指标 ${indicatorName} 已删除`
      }
    } catch (error) {
      return {
        success: false,
        error: error.message,
        message: '删除指标失败'
      }
    }
  }

  /**
   * 从index.js中移除指标注册
   */
  async removeFromIndexFile(cleanName, category) {
    // 这里应该实现从index.js中移除导入和注册语句的逻辑
    console.log(`从index.js中移除指标: ${cleanName}`)
  }
}

// 导出管理器实例
export const indicatorsManager = new IndicatorsManager()
export default IndicatorsManager