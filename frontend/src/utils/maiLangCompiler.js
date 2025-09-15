/**
 * 文华麦语言到JavaScript编译转换器
 * 支持VNPY指标格式输出和KLineChart集成
 * 基于MyTT库的函数映射实现
 */

// 麦语言基础函数映射到JavaScript实现
class MaiLangCompiler {
  constructor() {
    // 初始化函数映射表
    this.functionMap = this.initFunctionMap();
    // 操作符映射
    this.operatorMap = {
      ':=': '=',
      'AND': '&&',
      'OR': '||',
      'NOT': '!',
      '>=': '>=',
      '<=': '<=',
      '>': '>',
      '<': '<',
      '=': '===',
      '<>': '!=='
    };
    // 内置变量映射
    this.builtinVars = {
      'OPEN': 'data.open',
      'HIGH': 'data.high', 
      'LOW': 'data.low',
      'CLOSE': 'data.close',
      'VOL': 'data.volume',
      'VOLUME': 'data.volume',
      'O': 'data.open',
      'H': 'data.high',
      'L': 'data.low', 
      'C': 'data.close',
      'V': 'data.volume'
    };
  }

  // 初始化函数映射表（基于MyTT库）
  initFunctionMap() {
    return {
      // 基础数学函数
      'ABS': 'Math.abs',
      'MAX': 'Math.max',
      'MIN': 'Math.min',
      'SQRT': 'Math.sqrt',
      'POW': 'Math.pow',
      'LN': 'Math.log',
      'SIN': 'Math.sin',
      'COS': 'Math.cos',
      'TAN': 'Math.tan',
      
      // 序列处理函数
      'MA': 'this.MA',
      'EMA': 'this.EMA', 
      'SMA': 'this.SMA',
      'WMA': 'this.WMA',
      'REF': 'this.REF',
      'SUM': 'this.SUM',
      'STD': 'this.STD',
      'HHV': 'this.HHV',
      'LLV': 'this.LLV',
      'COUNT': 'this.COUNT',
      'EVERY': 'this.EVERY',
      'EXIST': 'this.EXIST',
      'CROSS': 'this.CROSS',
      'BARSLAST': 'this.BARSLAST',
      'IF': 'this.IF',
      
      // 技术指标函数
      'MACD': 'this.MACD',
      'KDJ': 'this.KDJ', 
      'RSI': 'this.RSI',
      'BOLL': 'this.BOLL',
      'ATR': 'this.ATR',
      'CCI': 'this.CCI',
      'WR': 'this.WR',
      'BIAS': 'this.BIAS',
      'PSY': 'this.PSY',
      'DMI': 'this.DMI'
    };
  }

  /**
   * 编译麦语言代码到JavaScript
   * @param {string} maiLangCode - 麦语言源代码
   * @returns {object} 编译结果
   */
  compile(maiLangCode) {
    try {
      // 预处理：去除注释和空行
      const cleanCode = this.preprocess(maiLangCode);
      
      // 词法分析
      const tokens = this.tokenize(cleanCode);
      
      // 语法分析
      const ast = this.parse(tokens);
      
      // 代码生成
      const jsCode = this.generateCode(ast);
      
      // 生成VNPY兼容的指标定义
      const vnpyIndicator = this.generateVNPYIndicator(ast);
      
      // 生成KLineChart兼容的指标定义
      const klineIndicator = this.generateKLineIndicator(ast);
      
      // 生成indicators文件夹兼容的格式
      const indicatorsFormat = this.generateIndicatorsFormat(ast);
      
      return {
        success: true,
        jsCode,
        vnpyIndicator,
        klineIndicator,
        indicatorsFormat,
        ast
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        line: error.line || 0,
        column: error.column || 0
      };
    }
  }

  /**
   * 生成indicators文件夹兼容的格式
   */
  generateIndicatorsFormat(ast) {
    const outputs = ast.outputs;
    const params = this.extractParameters(ast);
    
    // 判断是主图还是副图指标
    const isMainChart = this.isMainChartIndicator(outputs);
    
    return {
      name: 'customIndicator',
      shortName: 'CUSTOM',
      calcParams: params.map((value, index) => ({
        name: `param${index + 1}`,
        value: value,
        type: 'number'
      })),
      figures: outputs.map((name, index) => ({
        key: name.toLowerCase(),
        title: name,
        type: 'line',
        baseValue: isMainChart ? null : 0,
        styles: {
          style: 'solid',
          smooth: false,
          size: 1,
          color: this.getDefaultColor(name)
        }
      })),
      calc: this.generateIndicatorsCalcFunction(ast),
      regenerateFigures: null,
      createTooltipDataSource: null,
      draw: null
    };
  }

  /**
   * 判断是否为主图指标
   */
  isMainChartIndicator(outputs) {
    const mainChartKeywords = ['MA', 'EMA', 'SMA', 'BOLL', 'UP', 'DOWN', 'MID'];
    return outputs.some(output => 
      mainChartKeywords.some(keyword => output.toUpperCase().includes(keyword))
    );
  }

  /**
   * 生成indicators计算函数
   */
  generateIndicatorsCalcFunction(ast) {
    return `function(dataList, calcParams) {
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
    
    ${ast.statements.map(stmt => this.generateIndicatorsStatement(stmt)).join('\n    ')}
    
    result.push(indicatorData);
  }
  
  return result;
}`;
  }

  /**
   * 生成indicators语句
   */
  generateIndicatorsStatement(node) {
    if (node.type === 'Assignment') {
      return `indicatorData.${node.left.name.toLowerCase()} = ${this.generateExpression(node.right)};`;
    }
    return '';
  }

  /**
   * 预处理麦语言代码
   */
  preprocess(code) {
    return code
      .split('\n')
      .map(line => {
        // 移除注释
        const commentIndex = line.indexOf('//');
        if (commentIndex !== -1) {
          line = line.substring(0, commentIndex);
        }
        return line.trim();
      })
      .filter(line => line.length > 0)
      .join('\n');
  }

  /**
   * 词法分析
   */
  tokenize(code) {
    const tokens = [];
    const lines = code.split('\n');
    
    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
      const line = lines[lineNum];
      let pos = 0;
      
      while (pos < line.length) {
        const char = line[pos];
        
        // 跳过空白字符
        if (/\s/.test(char)) {
          pos++;
          continue;
        }
        
        // 识别数字
        if (/\d/.test(char)) {
          let num = '';
          while (pos < line.length && /[\d.]/.test(line[pos])) {
            num += line[pos++];
          }
          tokens.push({ type: 'NUMBER', value: parseFloat(num), line: lineNum, pos });
          continue;
        }
        
        // 识别标识符和关键字
        if (/[a-zA-Z_]/.test(char)) {
          let identifier = '';
          while (pos < line.length && /[a-zA-Z0-9_]/.test(line[pos])) {
            identifier += line[pos++];
          }
          
          const type = this.isKeyword(identifier) ? 'KEYWORD' : 'IDENTIFIER';
          tokens.push({ type, value: identifier, line: lineNum, pos });
          continue;
        }
        
        // 识别操作符
        const operator = this.matchOperator(line, pos);
        if (operator) {
          tokens.push({ type: 'OPERATOR', value: operator, line: lineNum, pos });
          pos += operator.length;
          continue;
        }
        
        // 识别分隔符
        if ('(),;'.includes(char)) {
          tokens.push({ type: 'DELIMITER', value: char, line: lineNum, pos });
          pos++;
          continue;
        }
        
        throw new Error(`Unexpected character '${char}' at line ${lineNum + 1}, position ${pos + 1}`);
      }
    }
    
    return tokens;
  }

  /**
   * 检查是否为关键字
   */
  isKeyword(word) {
    const keywords = ['IF', 'THEN', 'ELSE', 'AND', 'OR', 'NOT', 'TRUE', 'FALSE'];
    return keywords.includes(word.toUpperCase());
  }

  /**
   * 匹配操作符
   */
  matchOperator(line, pos) {
    const operators = [':=', '>=', '<=', '<>', '==', '&&', '||', '+', '-', '*', '/', '>', '<', '=', '!'];
    
    for (const op of operators) {
      if (line.substring(pos, pos + op.length) === op) {
        return op;
      }
    }
    return null;
  }

  /**
   * 语法分析
   */
  parse(tokens) {
    const ast = {
      type: 'Program',
      statements: [],
      variables: new Map(),
      outputs: []
    };
    
    let pos = 0;
    
    while (pos < tokens.length) {
      const statement = this.parseStatement(tokens, pos);
      ast.statements.push(statement.node);
      pos = statement.nextPos;
      
      // 收集变量定义和输出
      if (statement.node.type === 'Assignment') {
        ast.variables.set(statement.node.left.name, statement.node);
        
        // 检查是否为输出变量（通常以大写字母开头或特定命名）
        if (this.isOutputVariable(statement.node.left.name)) {
          ast.outputs.push(statement.node.left.name);
        }
      }
    }
    
    return ast;
  }

  /**
   * 解析语句
   */
  parseStatement(tokens, pos) {
    const token = tokens[pos];
    
    if (token.type === 'IDENTIFIER') {
      // 检查是否为赋值语句
      if (pos + 1 < tokens.length && tokens[pos + 1].value === ':=') {
        return this.parseAssignment(tokens, pos);
      }
    }
    
    throw new Error(`Unexpected token '${token.value}' at line ${token.line + 1}`);
  }

  /**
   * 解析赋值语句
   */
  parseAssignment(tokens, pos) {
    const identifier = tokens[pos];
    pos += 2; // 跳过标识符和 ':='
    
    const expression = this.parseExpression(tokens, pos);
    
    return {
      node: {
        type: 'Assignment',
        left: { type: 'Identifier', name: identifier.value },
        right: expression.node
      },
      nextPos: expression.nextPos
    };
  }

  /**
   * 解析表达式
   */
  parseExpression(tokens, pos) {
    return this.parseLogicalOr(tokens, pos);
  }

  /**
   * 解析逻辑或表达式
   */
  parseLogicalOr(tokens, pos) {
    let left = this.parseLogicalAnd(tokens, pos);
    pos = left.nextPos;
    
    while (pos < tokens.length && tokens[pos].value === 'OR') {
      pos++; // 跳过 'OR'
      const right = this.parseLogicalAnd(tokens, pos);
      left = {
        node: {
          type: 'BinaryExpression',
          operator: '||',
          left: left.node,
          right: right.node
        },
        nextPos: right.nextPos
      };
      pos = right.nextPos;
    }
    
    return left;
  }

  /**
   * 解析逻辑与表达式
   */
  parseLogicalAnd(tokens, pos) {
    let left = this.parseComparison(tokens, pos);
    pos = left.nextPos;
    
    while (pos < tokens.length && tokens[pos].value === 'AND') {
      pos++; // 跳过 'AND'
      const right = this.parseComparison(tokens, pos);
      left = {
        node: {
          type: 'BinaryExpression',
          operator: '&&',
          left: left.node,
          right: right.node
        },
        nextPos: right.nextPos
      };
      pos = right.nextPos;
    }
    
    return left;
  }

  /**
   * 解析比较表达式
   */
  parseComparison(tokens, pos) {
    let left = this.parseArithmetic(tokens, pos);
    pos = left.nextPos;
    
    const comparisonOps = ['>=', '<=', '>', '<', '=', '<>'];
    
    while (pos < tokens.length && comparisonOps.includes(tokens[pos].value)) {
      const operator = this.operatorMap[tokens[pos].value] || tokens[pos].value;
      pos++;
      const right = this.parseArithmetic(tokens, pos);
      left = {
        node: {
          type: 'BinaryExpression',
          operator,
          left: left.node,
          right: right.node
        },
        nextPos: right.nextPos
      };
      pos = right.nextPos;
    }
    
    return left;
  }

  /**
   * 解析算术表达式
   */
  parseArithmetic(tokens, pos) {
    let left = this.parseTerm(tokens, pos);
    pos = left.nextPos;
    
    while (pos < tokens.length && ['+', '-'].includes(tokens[pos].value)) {
      const operator = tokens[pos].value;
      pos++;
      const right = this.parseTerm(tokens, pos);
      left = {
        node: {
          type: 'BinaryExpression',
          operator,
          left: left.node,
          right: right.node
        },
        nextPos: right.nextPos
      };
      pos = right.nextPos;
    }
    
    return left;
  }

  /**
   * 解析项
   */
  parseTerm(tokens, pos) {
    let left = this.parseFactor(tokens, pos);
    pos = left.nextPos;
    
    while (pos < tokens.length && ['*', '/'].includes(tokens[pos].value)) {
      const operator = tokens[pos].value;
      pos++;
      const right = this.parseFactor(tokens, pos);
      left = {
        node: {
          type: 'BinaryExpression',
          operator,
          left: left.node,
          right: right.node
        },
        nextPos: right.nextPos
      };
      pos = right.nextPos;
    }
    
    return left;
  }

  /**
   * 解析因子
   */
  parseFactor(tokens, pos) {
    const token = tokens[pos];
    
    if (token.type === 'NUMBER') {
      return {
        node: { type: 'Literal', value: token.value },
        nextPos: pos + 1
      };
    }
    
    if (token.type === 'IDENTIFIER') {
      // 检查是否为函数调用
      if (pos + 1 < tokens.length && tokens[pos + 1].value === '(') {
        return this.parseFunctionCall(tokens, pos);
      }
      
      // 普通标识符
      return {
        node: { type: 'Identifier', name: token.value },
        nextPos: pos + 1
      };
    }
    
    if (token.value === '(') {
      pos++; // 跳过 '('
      const expression = this.parseExpression(tokens, pos);
      pos = expression.nextPos;
      
      if (pos >= tokens.length || tokens[pos].value !== ')') {
        throw new Error(`Expected ')' at line ${token.line + 1}`);
      }
      
      return {
        node: expression.node,
        nextPos: pos + 1
      };
    }
    
    throw new Error(`Unexpected token '${token.value}' at line ${token.line + 1}`);
  }

  /**
   * 解析函数调用
   */
  parseFunctionCall(tokens, pos) {
    const functionName = tokens[pos].value;
    pos += 2; // 跳过函数名和 '('
    
    const args = [];
    
    while (pos < tokens.length && tokens[pos].value !== ')') {
      const arg = this.parseExpression(tokens, pos);
      args.push(arg.node);
      pos = arg.nextPos;
      
      if (pos < tokens.length && tokens[pos].value === ',') {
        pos++; // 跳过 ','
      }
    }
    
    if (pos >= tokens.length || tokens[pos].value !== ')') {
      throw new Error(`Expected ')' for function ${functionName}`);
    }
    
    return {
      node: {
        type: 'FunctionCall',
        name: functionName,
        arguments: args
      },
      nextPos: pos + 1
    };
  }

  /**
   * 检查是否为输出变量
   */
  isOutputVariable(name) {
    // 通常输出变量以大写字母开头或包含特定关键字
    return /^[A-Z]/.test(name) || 
           ['MA', 'EMA', 'MACD', 'KDJ', 'RSI', 'BOLL', 'UP', 'DOWN', 'MID'].some(keyword => 
             name.includes(keyword)
           );
  }

  /**
   * 生成JavaScript代码
   */
  generateCode(ast) {
    let code = `
// 生成的JavaScript指标代码
function calculateIndicator(data) {
  const result = {};
  
`;
    
    // 生成变量计算代码
    for (const statement of ast.statements) {
      code += '  ' + this.generateStatement(statement) + '\n';
    }
    
    // 返回输出变量
    if (ast.outputs.length > 0) {
      code += '\n  return {\n';
      for (const output of ast.outputs) {
        code += `    ${output}: ${output},\n`;
      }
      code += '  };\n';
    }
    
    code += '}\n';
    
    return code;
  }

  /**
   * 生成语句代码
   */
  generateStatement(node) {
    switch (node.type) {
      case 'Assignment':
        return `const ${node.left.name} = ${this.generateExpression(node.right)};`;
      default:
        throw new Error(`Unknown statement type: ${node.type}`);
    }
  }

  /**
   * 生成表达式代码
   */
  generateExpression(node) {
    switch (node.type) {
      case 'Literal':
        return node.value.toString();
      
      case 'Identifier':
        // 检查是否为内置变量
        if (this.builtinVars[node.name]) {
          return this.builtinVars[node.name];
        }
        return node.name;
      
      case 'BinaryExpression':
        return `(${this.generateExpression(node.left)} ${node.operator} ${this.generateExpression(node.right)})`;
      
      case 'FunctionCall':
        const jsFunction = this.functionMap[node.name.toUpperCase()];
        if (!jsFunction) {
          throw new Error(`Unknown function: ${node.name}`);
        }
        
        const args = node.arguments.map(arg => this.generateExpression(arg)).join(', ');
        return `${jsFunction}(${args})`;
      
      default:
        throw new Error(`Unknown expression type: ${node.type}`);
    }
  }

  /**
   * 生成VNPY兼容的指标定义
   */
  generateVNPYIndicator(ast) {
    const outputs = ast.outputs;
    
    return {
      name: 'CustomIndicator',
      parameters: this.extractParameters(ast),
      outputs: outputs.map(name => ({
        name,
        type: 'line',
        color: this.getDefaultColor(name)
      })),
      calculate: this.generateVNPYCalculateFunction(ast)
    };
  }

  /**
   * 生成KLineChart兼容的指标定义
   */
  generateKLineIndicator(ast) {
    const outputs = ast.outputs;
    
    return {
      name: 'customIndicator',
      shortName: 'CUSTOM',
      precision: 2,
      calcParams: this.extractParameters(ast),
      plots: outputs.map((name, index) => ({
        key: name.toLowerCase(),
        title: name,
        type: 'line',
        color: this.getDefaultColor(name),
        isStroke: true
      })),
      calc: this.generateKLineCalculateFunction(ast)
    };
  }

  /**
   * 提取参数
   */
  extractParameters(ast) {
    // 从AST中提取数字常量作为参数
    const params = [];
    
    const extractFromNode = (node) => {
      if (node.type === 'Literal' && typeof node.value === 'number') {
        if (!params.includes(node.value)) {
          params.push(node.value);
        }
      } else if (node.type === 'BinaryExpression') {
        extractFromNode(node.left);
        extractFromNode(node.right);
      } else if (node.type === 'FunctionCall') {
        node.arguments.forEach(extractFromNode);
      }
    };
    
    ast.statements.forEach(statement => {
      if (statement.type === 'Assignment') {
        extractFromNode(statement.right);
      }
    });
    
    return params.slice(0, 5); // 限制参数数量
  }

  /**
   * 获取默认颜色
   */
  getDefaultColor(name) {
    const colorMap = {
      'MA': '#FF6B35',
      'EMA': '#004E89', 
      'MACD': '#1A659E',
      'DIF': '#1A659E',
      'DEA': '#F77F00',
      'RSI': '#9B287B',
      'K': '#FF6B35',
      'D': '#004E89',
      'J': '#1A659E',
      'UP': '#FF6B35',
      'MID': '#004E89',
      'DOWN': '#1A659E'
    };
    
    for (const [key, color] of Object.entries(colorMap)) {
      if (name.includes(key)) {
        return color;
      }
    }
    
    return '#666666';
  }

  /**
   * 生成VNPY计算函数
   */
  generateVNPYCalculateFunction(ast) {
    return `
from typing import List, Dict, Any
from vnpy.trader.object import BarData
import numpy as np
import pandas as pd

def calculate_indicator(bars: List[BarData], params: Dict[str, Any]) -> Dict[str, List[float]]:
    """计算自定义指标"""
    if not bars:
        return {}
    
    # 提取价格数据
    opens = [bar.open_price for bar in bars]
    highs = [bar.high_price for bar in bars]
    lows = [bar.low_price for bar in bars]
    closes = [bar.close_price for bar in bars]
    volumes = [bar.volume for bar in bars]
    
    # 转换为numpy数组
    data = {
        'open': np.array(opens),
        'high': np.array(highs),
        'low': np.array(lows),
        'close': np.array(closes),
        'volume': np.array(volumes)
    }
    
    result = {}
    
    ${ast.statements.map(stmt => this.generateVNPYStatement(stmt)).join('\n    ')}
    
    return result
`;
  }

  /**
   * 生成KLineChart计算函数
   */
  generateKLineCalculateFunction(ast) {
    return `
function(dataList, calcParams, plots) {
  const result = [];
  
  for (let i = 0; i < dataList.length; i++) {
    const data = {
      open: dataList.map(d => d.open),
      high: dataList.map(d => d.high),
      low: dataList.map(d => d.low),
      close: dataList.map(d => d.close),
      volume: dataList.map(d => d.volume)
    };
    
    const indicatorData = {};
    
    ${ast.statements.map(stmt => this.generateKLineStatement(stmt)).join('\n    ')}
    
    result.push(indicatorData);
  }
  
  return result;
}
`;
  }

  /**
   * 生成VNPY语句
   */
  generateVNPYStatement(node) {
    if (node.type === 'Assignment') {
      return `result['${node.left.name}'] = ${this.generateVNPYExpression(node.right)}`;
    }
    return '';
  }

  /**
   * 生成KLineChart语句
   */
  generateKLineStatement(node) {
    if (node.type === 'Assignment') {
      return `indicatorData.${node.left.name.toLowerCase()} = ${this.generateExpression(node.right)}`;
    }
    return '';
  }

  /**
   * 生成VNPY表达式
   */
  generateVNPYExpression(node) {
    switch (node.type) {
      case 'Literal':
        return node.value.toString();
      
      case 'Identifier':
        const pythonVar = {
          'OPEN': 'data["open"]',
          'HIGH': 'data["high"]', 
          'LOW': 'data["low"]',
          'CLOSE': 'data["close"]',
          'VOL': 'data["volume"]',
          'VOLUME': 'data["volume"]'
        };
        return pythonVar[node.name] || node.name;
      
      case 'BinaryExpression':
        return `(${this.generateVNPYExpression(node.left)} ${node.operator} ${this.generateVNPYExpression(node.right)})`;
      
      case 'FunctionCall':
        // 映射到Python函数
        const pythonFunction = this.getPythonFunction(node.name);
        const args = node.arguments.map(arg => this.generateVNPYExpression(arg)).join(', ');
        return `${pythonFunction}(${args})`;
      
      default:
        return '';
    }
  }

  /**
   * 获取Python函数映射
   */
  getPythonFunction(funcName) {
    const pythonMap = {
      'MA': 'talib.SMA',
      'EMA': 'talib.EMA',
      'SMA': 'talib.SMA',
      'RSI': 'talib.RSI',
      'MACD': 'talib.MACD',
      'BOLL': 'talib.BBANDS',
      'ATR': 'talib.ATR',
      'MAX': 'np.maximum',
      'MIN': 'np.minimum',
      'ABS': 'np.abs',
      'SUM': 'np.sum'
    };
    
    return pythonMap[funcName.toUpperCase()] || `custom_${funcName.toLowerCase()}`;
  }
}

// 导出编译器
export default MaiLangCompiler;

// 导出编译器实例
export const maiLangCompiler = new MaiLangCompiler();