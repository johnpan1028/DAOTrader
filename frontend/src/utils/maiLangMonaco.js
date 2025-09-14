/**
 * 麦语言Monaco Editor配置
 * 提供语法高亮、智能提示、错误检查等功能
 */

// 麦语言关键字
const MAI_KEYWORDS = [
  // 基础函数
  'MA', 'EMA', 'SMA', 'WMA', 'DMA',
  'MACD', 'KDJ', 'RSI', 'BOLL', 'ATR',
  'CCI', 'ROC', 'BIAS', 'PSY', 'VR',
  'WR', 'SAR', 'DMI', 'TRIX', 'OBV',
  
  // K线数据函数
  'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOL',
  'AMOUNT', 'AVPRICE',
  
  // 引用函数
  'REF', 'LLV', 'HHV', 'LLVBARS', 'HHVBARS',
  'COUNT', 'SUM', 'ABS', 'MAX', 'MIN',
  
  // 逻辑函数
  'IF', 'IFF', 'IFS', 'BETWEEN', 'CROSS',
  'LONGCROSS', 'UPNDAY', 'DOWNNDAY',
  
  // 数学函数
  'SQRT', 'POW', 'LOG', 'LN', 'EXP',
  'SIN', 'COS', 'TAN', 'ASIN', 'ACOS', 'ATAN',
  'ROUND', 'CEILING', 'FLOOR', 'MOD',
  
  // 统计函数
  'STD', 'VAR', 'CORR', 'COVAR',
  
  // 时间函数
  'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE',
  'WEEKDAY', 'DATE', 'TIME',
  
  // 条件函数
  'EVERY', 'EXIST', 'LAST', 'SINCE',
  
  // 画图函数
  'DRAWLINE', 'DRAWTEXT', 'DRAWICON',
  'STICKLINE', 'POLYLINE',
  
  // 颜色常量
  'COLORRED', 'COLORGREEN', 'COLORBLUE',
  'COLORYELLOW', 'COLORMAGENTA', 'COLORCYAN',
  'COLORWHITE', 'COLORBLACK', 'COLORGRAY',
  
  // 线型常量
  'LINETHICK1', 'LINETHICK2', 'LINETHICK3',
  'LINETHICK4', 'LINETHICK5', 'LINETHICK6',
  'LINETHICK7', 'LINETHICK8', 'LINETHICK9',
  'POINTDOT', 'STICK', 'COLORSTICK',
  
  // 其他常量
  'DRAWNULL', 'EMPTY', 'CONST'
]

// 麦语言操作符
const MAI_OPERATORS = [
  '+', '-', '*', '/', '%',
  '=', '<>', '>', '<', '>=', '<=',
  'AND', 'OR', 'NOT',
  '&&', '||', '!',
  ':=', ':', ';',
  '(', ')', '[', ']', '{', '}',
  ',', '.'
]

// 内置常量
const MAI_CONSTANTS = [
  'TRUE', 'FALSE', 'NULL', 'EMPTY',
  'PI', 'E'
]

/**
 * 注册麦语言到Monaco Editor
 */
export function registerMaiLanguage() {
  // 注册语言
  monaco.languages.register({ id: 'mai-lang' })
  
  // 设置语法高亮
  monaco.languages.setMonarchTokensProvider('mai-lang', {
    keywords: MAI_KEYWORDS,
    operators: MAI_OPERATORS,
    constants: MAI_CONSTANTS,
    
    // 符号定义
    symbols: /[=><!~?:&|+\-*\/\^%]+/,
    
    // 转义序列
    escapes: /\\(?:[abfnrtv\\"']|x[0-9A-Fa-f]{1,4}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,
    
    // 词法规则
    tokenizer: {
      root: [
        // 标识符和关键字
        [/[a-zA-Z_]\w*/, {
          cases: {
            '@keywords': 'keyword',
            '@constants': 'constant',
            '@default': 'identifier'
          }
        }],
        
        // 数字
        [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
        [/\d+/, 'number'],
        
        // 字符串
        [/"([^"\\]|\\.)*$/, 'string.invalid'],  // 未闭合字符串
        [/"/, { token: 'string.quote', bracket: '@open', next: '@string' }],
        [/'([^'\\]|\\.)*$/, 'string.invalid'],  // 未闭合字符串
        [/'/, { token: 'string.quote', bracket: '@open', next: '@string_single' }],
        
        // 注释
        [/\/\/.*$/, 'comment'],
        [/\/\*/, 'comment', '@comment'],
        [/\{.*?\}/, 'comment'],  // 麦语言注释格式
        
        // 操作符
        [/@symbols/, {
          cases: {
            '@operators': 'operator',
            '@default': ''
          }
        }],
        
        // 分隔符
        [/[;,.]/, 'delimiter'],
        [/[()\[\]]/, '@brackets'],
        
        // 空白字符
        [/[ \t\r\n]+/, 'white']
      ],
      
      // 字符串处理
      string: [
        [/[^\\"]+/, 'string'],
        [/@escapes/, 'string.escape'],
        [/\\./, 'string.escape.invalid'],
        [/"/, { token: 'string.quote', bracket: '@close', next: '@pop' }]
      ],
      
      string_single: [
        [/[^\\']+/, 'string'],
        [/@escapes/, 'string.escape'],
        [/\\./, 'string.escape.invalid'],
        [/'/, { token: 'string.quote', bracket: '@close', next: '@pop' }]
      ],
      
      // 注释处理
      comment: [
        [/[^\/*]+/, 'comment'],
        [/\*\//, 'comment', '@pop'],
        [/[\/*]/, 'comment']
      ]
    }
  })
  
  // 设置语言配置
  monaco.languages.setLanguageConfiguration('mai-lang', {
    comments: {
      lineComment: '//',
      blockComment: ['/*', '*/'],
      blockComment: ['{', '}']
    },
    brackets: [
      ['{', '}'],
      ['[', ']'],
      ['(', ')']
    ],
    autoClosingPairs: [
      { open: '{', close: '}' },
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ],
    surroundingPairs: [
      { open: '{', close: '}' },
      { open: '[', close: ']' },
      { open: '(', close: ')' },
      { open: '"', close: '"' },
      { open: "'", close: "'" }
    ],
    folding: {
      markers: {
        start: new RegExp('^\\s*{\\s*$'),
        end: new RegExp('^\\s*}\\s*$')
      }
    }
  })
}

/**
 * 创建智能提示提供器
 */
export function createCompletionProvider() {
  return monaco.languages.registerCompletionItemProvider('mai-lang', {
    provideCompletionItems: (model, position) => {
      const word = model.getWordUntilPosition(position)
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn
      }
      
      const suggestions = []
      
      // 关键字提示
      MAI_KEYWORDS.forEach(keyword => {
        suggestions.push({
          label: keyword,
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: keyword,
          range: range,
          documentation: getFunctionDocumentation(keyword)
        })
      })
      
      // 常用模板提示
      const templates = getCodeTemplates()
      templates.forEach(template => {
        suggestions.push({
          label: template.label,
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: template.insertText,
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          range: range,
          documentation: template.documentation
        })
      })
      
      return { suggestions }
    }
  })
}

/**
 * 创建悬停提示提供器
 */
export function createHoverProvider() {
  return monaco.languages.registerHoverProvider('mai-lang', {
    provideHover: (model, position) => {
      const word = model.getWordAtPosition(position)
      if (!word) return null
      
      const documentation = getFunctionDocumentation(word.word)
      if (!documentation) return null
      
      return {
        range: new monaco.Range(
          position.lineNumber,
          word.startColumn,
          position.lineNumber,
          word.endColumn
        ),
        contents: [
          { value: `**${word.word}**` },
          { value: documentation }
        ]
      }
    }
  })
}

/**
 * 创建签名帮助提供器
 */
export function createSignatureHelpProvider() {
  return monaco.languages.registerSignatureHelpProvider('mai-lang', {
    signatureHelpTriggerCharacters: ['(', ','],
    provideSignatureHelp: (model, position) => {
      // 查找当前函数调用
      const lineContent = model.getLineContent(position.lineNumber)
      const beforeCursor = lineContent.substring(0, position.column - 1)
      
      // 简单的函数名匹配
      const functionMatch = beforeCursor.match(/([A-Z_]\w*)\s*\([^)]*$/)
      if (!functionMatch) return null
      
      const functionName = functionMatch[1]
      const signature = getFunctionSignature(functionName)
      if (!signature) return null
      
      // 计算当前参数位置
      const parameterIndex = (beforeCursor.match(/,/g) || []).length
      
      return {
        value: {
          signatures: [{
            label: signature.label,
            documentation: signature.documentation,
            parameters: signature.parameters
          }],
          activeSignature: 0,
          activeParameter: Math.min(parameterIndex, signature.parameters.length - 1)
        },
        dispose: () => {}
      }
    }
  })
}

/**
 * 创建诊断提供器（错误检查）
 */
export function createDiagnosticsProvider() {
  return {
    validateCode: (model) => {
      const markers = []
      const content = model.getValue()
      const lines = content.split('\n')
      
      lines.forEach((line, lineIndex) => {
        // 检查语法错误
        const syntaxErrors = checkSyntaxErrors(line, lineIndex + 1)
        markers.push(...syntaxErrors)
        
        // 检查未定义函数
        const undefinedFunctions = checkUndefinedFunctions(line, lineIndex + 1)
        markers.push(...undefinedFunctions)
        
        // 检查参数数量
        const parameterErrors = checkParameterCount(line, lineIndex + 1)
        markers.push(...parameterErrors)
      })
      
      monaco.editor.setModelMarkers(model, 'mai-lang', markers)
    }
  }
}

/**
 * 获取函数文档
 */
function getFunctionDocumentation(functionName) {
  const docs = {
    'MA': '移动平均线\n语法: MA(X, N)\n参数: X-数据序列, N-周期\n返回: N周期移动平均值',
    'EMA': '指数移动平均线\n语法: EMA(X, N)\n参数: X-数据序列, N-周期\n返回: N周期指数移动平均值',
    'MACD': 'MACD指标\n语法: MACD(CLOSE, SHORT, LONG, MID)\n参数: CLOSE-收盘价, SHORT-短周期, LONG-长周期, MID-信号线周期\n返回: DIF, DEA, MACD',
    'RSI': '相对强弱指标\n语法: RSI(X, N)\n参数: X-数据序列, N-周期\n返回: RSI值(0-100)',
    'KDJ': 'KDJ随机指标\n语法: KDJ(HIGH, LOW, CLOSE, N, M1, M2)\n参数: HIGH-最高价, LOW-最低价, CLOSE-收盘价, N-RSV周期, M1-K值周期, M2-D值周期\n返回: K, D, J',
    'BOLL': '布林带指标\n语法: BOLL(X, N, P)\n参数: X-数据序列, N-周期, P-标准差倍数\n返回: UPPER, MID, LOWER',
    'ATR': '真实波动幅度\n语法: ATR(HIGH, LOW, CLOSE, N)\n参数: HIGH-最高价, LOW-最低价, CLOSE-收盘价, N-周期\n返回: ATR值',
    'OPEN': '开盘价\n返回: 当前K线的开盘价',
    'HIGH': '最高价\n返回: 当前K线的最高价',
    'LOW': '最低价\n返回: 当前K线的最低价',
    'CLOSE': '收盘价\n返回: 当前K线的收盘价',
    'VOL': '成交量\n返回: 当前K线的成交量',
    'REF': '引用函数\n语法: REF(X, A)\n参数: X-数据序列, A-引用周期数\n返回: A周期前的X值',
    'HHV': '最高值\n语法: HHV(X, N)\n参数: X-数据序列, N-周期\n返回: N周期内X的最高值',
    'LLV': '最低值\n语法: LLV(X, N)\n参数: X-数据序列, N-周期\n返回: N周期内X的最低值',
    'SUM': '求和\n语法: SUM(X, N)\n参数: X-数据序列, N-周期\n返回: N周期内X的累计和',
    'COUNT': '计数\n语法: COUNT(X, N)\n参数: X-条件表达式, N-周期\n返回: N周期内满足条件X的次数',
    'IF': '条件函数\n语法: IF(COND, A, B)\n参数: COND-条件, A-真值, B-假值\n返回: 条件为真返回A，否则返回B',
    'CROSS': '交叉函数\n语法: CROSS(A, B)\n参数: A-序列1, B-序列2\n返回: A向上穿越B时返回1，否则返回0'
  }
  
  return docs[functionName] || null
}

/**
 * 获取函数签名
 */
function getFunctionSignature(functionName) {
  const signatures = {
    'MA': {
      label: 'MA(X, N)',
      documentation: '移动平均线',
      parameters: [
        { label: 'X', documentation: '数据序列' },
        { label: 'N', documentation: '周期' }
      ]
    },
    'EMA': {
      label: 'EMA(X, N)',
      documentation: '指数移动平均线',
      parameters: [
        { label: 'X', documentation: '数据序列' },
        { label: 'N', documentation: '周期' }
      ]
    },
    'MACD': {
      label: 'MACD(CLOSE, SHORT, LONG, MID)',
      documentation: 'MACD指标',
      parameters: [
        { label: 'CLOSE', documentation: '收盘价序列' },
        { label: 'SHORT', documentation: '短周期，默认12' },
        { label: 'LONG', documentation: '长周期，默认26' },
        { label: 'MID', documentation: '信号线周期，默认9' }
      ]
    },
    'RSI': {
      label: 'RSI(X, N)',
      documentation: '相对强弱指标',
      parameters: [
        { label: 'X', documentation: '数据序列' },
        { label: 'N', documentation: '周期，默认14' }
      ]
    },
    'KDJ': {
      label: 'KDJ(HIGH, LOW, CLOSE, N, M1, M2)',
      documentation: 'KDJ随机指标',
      parameters: [
        { label: 'HIGH', documentation: '最高价序列' },
        { label: 'LOW', documentation: '最低价序列' },
        { label: 'CLOSE', documentation: '收盘价序列' },
        { label: 'N', documentation: 'RSV周期，默认9' },
        { label: 'M1', documentation: 'K值周期，默认3' },
        { label: 'M2', documentation: 'D值周期，默认3' }
      ]
    },
    'BOLL': {
      label: 'BOLL(X, N, P)',
      documentation: '布林带指标',
      parameters: [
        { label: 'X', documentation: '数据序列' },
        { label: 'N', documentation: '周期，默认20' },
        { label: 'P', documentation: '标准差倍数，默认2' }
      ]
    },
    'IF': {
      label: 'IF(COND, A, B)',
      documentation: '条件函数',
      parameters: [
        { label: 'COND', documentation: '条件表达式' },
        { label: 'A', documentation: '条件为真时的返回值' },
        { label: 'B', documentation: '条件为假时的返回值' }
      ]
    }
  }
  
  return signatures[functionName] || null
}

/**
 * 获取代码模板
 */
function getCodeTemplates() {
  return [
    {
      label: 'ma-template',
      insertText: 'MA${1:5}: MA(CLOSE, ${1:5});\nMA${2:10}: MA(CLOSE, ${2:10});',
      documentation: '双均线模板'
    },
    {
      label: 'macd-template',
      insertText: 'DIF: MACD(CLOSE, ${1:12}, ${2:26}, ${3:9})[0];\nDEA: MACD(CLOSE, ${1:12}, ${2:26}, ${3:9})[1];\nMACD: MACD(CLOSE, ${1:12}, ${2:26}, ${3:9})[2];',
      documentation: 'MACD指标模板'
    },
    {
      label: 'rsi-template',
      insertText: 'RSI${1:14}: RSI(CLOSE, ${1:14});',
      documentation: 'RSI指标模板'
    },
    {
      label: 'kdj-template',
      insertText: 'K: KDJ(HIGH, LOW, CLOSE, ${1:9}, ${2:3}, ${3:3})[0];\nD: KDJ(HIGH, LOW, CLOSE, ${1:9}, ${2:3}, ${3:3})[1];\nJ: KDJ(HIGH, LOW, CLOSE, ${1:9}, ${2:3}, ${3:3})[2];',
      documentation: 'KDJ指标模板'
    },
    {
      label: 'boll-template',
      insertText: 'UPPER: BOLL(CLOSE, ${1:20}, ${2:2})[0];\nMID: BOLL(CLOSE, ${1:20}, ${2:2})[1];\nLOWER: BOLL(CLOSE, ${1:20}, ${2:2})[2];',
      documentation: '布林带指标模板'
    },
    {
      label: 'cross-template',
      insertText: 'BUY: CROSS(${1:MA5}, ${2:MA10});\nSELL: CROSS(${2:MA10}, ${1:MA5});',
      documentation: '交叉信号模板'
    }
  ]
}

/**
 * 检查语法错误
 */
function checkSyntaxErrors(line, lineNumber) {
  const errors = []
  
  // 检查括号匹配
  const openParens = (line.match(/\(/g) || []).length
  const closeParens = (line.match(/\)/g) || []).length
  if (openParens !== closeParens) {
    errors.push({
      severity: monaco.MarkerSeverity.Error,
      startLineNumber: lineNumber,
      startColumn: 1,
      endLineNumber: lineNumber,
      endColumn: line.length + 1,
      message: '括号不匹配'
    })
  }
  
  // 检查分号结尾
  const trimmedLine = line.trim()
  if (trimmedLine && !trimmedLine.endsWith(';') && !trimmedLine.startsWith('//') && !trimmedLine.startsWith('{')) {
    errors.push({
      severity: monaco.MarkerSeverity.Warning,
      startLineNumber: lineNumber,
      startColumn: line.length,
      endLineNumber: lineNumber,
      endColumn: line.length + 1,
      message: '建议以分号结尾'
    })
  }
  
  return errors
}

/**
 * 检查未定义函数
 */
function checkUndefinedFunctions(line, lineNumber) {
  const errors = []
  
  // 匹配函数调用
  const functionCalls = line.match(/([A-Z_]\w*)\s*\(/g)
  if (functionCalls) {
    functionCalls.forEach(call => {
      const functionName = call.replace(/\s*\($/, '')
      if (!MAI_KEYWORDS.includes(functionName)) {
        const startColumn = line.indexOf(call) + 1
        errors.push({
          severity: monaco.MarkerSeverity.Warning,
          startLineNumber: lineNumber,
          startColumn: startColumn,
          endLineNumber: lineNumber,
          endColumn: startColumn + functionName.length,
          message: `未知函数: ${functionName}`
        })
      }
    })
  }
  
  return errors
}

/**
 * 检查参数数量
 */
function checkParameterCount(line, lineNumber) {
  const errors = []
  
  // 简单的参数数量检查
  const functionMatches = line.match(/([A-Z_]\w*)\s*\(([^)]*)\)/g)
  if (functionMatches) {
    functionMatches.forEach(match => {
      const [, functionName, params] = match.match(/([A-Z_]\w*)\s*\(([^)]*)\)/)
      const paramCount = params.trim() ? params.split(',').length : 0
      
      const expectedParams = getExpectedParameterCount(functionName)
      if (expectedParams && (paramCount < expectedParams.min || paramCount > expectedParams.max)) {
        const startColumn = line.indexOf(match) + 1
        errors.push({
          severity: monaco.MarkerSeverity.Error,
          startLineNumber: lineNumber,
          startColumn: startColumn,
          endLineNumber: lineNumber,
          endColumn: startColumn + match.length,
          message: `${functionName}函数参数数量错误，期望${expectedParams.min}-${expectedParams.max}个，实际${paramCount}个`
        })
      }
    })
  }
  
  return errors
}

/**
 * 获取期望的参数数量
 */
function getExpectedParameterCount(functionName) {
  const paramCounts = {
    'MA': { min: 2, max: 2 },
    'EMA': { min: 2, max: 2 },
    'SMA': { min: 2, max: 2 },
    'MACD': { min: 1, max: 4 },
    'RSI': { min: 1, max: 2 },
    'KDJ': { min: 3, max: 6 },
    'BOLL': { min: 1, max: 3 },
    'ATR': { min: 3, max: 4 },
    'REF': { min: 2, max: 2 },
    'HHV': { min: 2, max: 2 },
    'LLV': { min: 2, max: 2 },
    'SUM': { min: 2, max: 2 },
    'COUNT': { min: 2, max: 2 },
    'IF': { min: 3, max: 3 },
    'CROSS': { min: 2, max: 2 }
  }
  
  return paramCounts[functionName] || null
}

/**
 * 设置编辑器主题
 */
export function setMaiLanguageTheme() {
  monaco.editor.defineTheme('mai-lang-theme', {
    base: 'vs',
    inherit: true,
    rules: [
      { token: 'keyword', foreground: '0000ff', fontStyle: 'bold' },
      { token: 'constant', foreground: '008080', fontStyle: 'bold' },
      { token: 'number', foreground: '098658' },
      { token: 'number.float', foreground: '098658' },
      { token: 'string', foreground: 'a31515' },
      { token: 'comment', foreground: '008000', fontStyle: 'italic' },
      { token: 'operator', foreground: '000000' },
      { token: 'identifier', foreground: '000000' },
      { token: 'delimiter', foreground: '000000' }
    ],
    colors: {
      'editor.background': 'var(--tv-bg-secondary)',
      'editor.foreground': '#000000',
      'editorLineNumber.foreground': '#237893',
      'editor.selectionBackground': '#add6ff',
      'editor.inactiveSelectionBackground': '#e5ebf1'
    }
  })
}

/**
 * 初始化麦语言Monaco Editor支持
 */
export function initializeMaiLanguageSupport() {
  registerMaiLanguage()
  createCompletionProvider()
  createHoverProvider()
  createSignatureHelpProvider()
  setMaiLanguageTheme()
  
  return createDiagnosticsProvider()
}