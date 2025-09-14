# 编程提示词 - 专用指标编程IDE (Coding AI) v1.0

## 项目概述

你是一个专业的前端开发工程师，负责开发一个专用的指标编程IDE。这个IDE允许用户通过简化的DSL语法编写技术指标，编译后生成klinechart能识别的JavaScript指标代码。

## 功能逻辑

### 核心功能模块

#### 1. DSL编译器模块
- **词法分析器(Lexer)**：将DSL源代码分解为Token序列
- **语法分析器(Parser)**：构建抽象语法树(AST)
- **语义分析器(Analyzer)**：类型检查和语义验证
- **代码生成器(Generator)**：生成klinechart兼容的JS代码

#### 2. IDE编辑器模块
- **Monaco Editor集成**：提供代码编辑功能
- **语法高亮**：DSL语法着色显示
- **智能提示**：函数和参数自动补全
- **错误检查**：实时语法和语义错误提示
- **代码预览**：显示编译后的JS代码

#### 3. 文件管理模块
- **DSL文件存储**：保存.dsl源文件
- **JS文件生成**：自动生成到indicators目录
- **文件列表管理**：显示和管理指标文件

### 数据流设计
```
DSL源码 → Lexer → Tokens → Parser → AST → Analyzer → 验证后AST → Generator → JS代码
    ↓                                                                        ↓
编辑器显示 ← 错误信息 ← 语义分析 ← 语法分析 ← 词法分析                    保存到文件系统
```

### 交互逻辑
1. **用户输入DSL代码** → 触发实时编译
2. **编译器处理** → 返回编译结果或错误信息
3. **IDE更新显示** → 错误标记、代码预览、智能提示
4. **用户保存** → 生成JS文件到indicators目录

## 接口定义

### DSL编译器接口

```typescript
// 编译器主接口
interface DSLCompiler {
  compile(source: string): CompileResult;
  validate(source: string): ValidationResult;
  getCompletions(source: string, position: Position): CompletionItem[];
}

// 编译结果
interface CompileResult {
  success: boolean;
  code?: string;           // 生成的JS代码
  errors: CompileError[];  // 编译错误
  warnings: CompileError[]; // 警告信息
  ast?: ProgramNode;       // 抽象语法树
}

// 编译错误
interface CompileError {
  type: 'lexical' | 'syntax' | 'semantic';
  message: string;
  line: number;
  column: number;
  length?: number;
  suggestion?: string;
}

// 自动补全项
interface CompletionItem {
  label: string;
  kind: CompletionItemKind;
  detail?: string;
  documentation?: string;
  insertText: string;
  insertTextRules?: InsertTextRule;
}
```

### IDE组件接口

```typescript
// 主编辑器组件
interface DSLEditorProps {
  modelValue: string;
  readonly?: boolean;
  theme?: 'light' | 'dark';
  fontSize?: number;
}

interface DSLEditorEmits {
  'update:modelValue': [value: string];
  'compile': [result: CompileResult];
  'save': [filename: string, content: string];
}

// 文件管理接口
interface FileManager {
  loadFile(path: string): Promise<string>;
  saveFile(path: string, content: string): Promise<void>;
  listFiles(directory: string): Promise<FileInfo[]>;
  deleteFile(path: string): Promise<void>;
}

interface FileInfo {
  name: string;
  path: string;
  type: 'dsl' | 'js';
  size: number;
  lastModified: Date;
}
```

## 数据库/存储

### 文件存储结构
```
DAOTrader/
├── indicators/
│   ├── dsl/                    # DSL源文件目录
│   │   ├── main/
│   │   │   ├── custom-ma.dsl
│   │   │   └── custom-ema.dsl
│   │   └── sub/
│   │       ├── custom-rsi.dsl
│   │       └── custom-macd.dsl
│   ├── main/                   # 生成的主图指标JS文件
│   │   ├── custom-ma.js
│   │   └── custom-ema.js
│   └── sub/                    # 生成的副图指标JS文件
│       ├── custom-rsi.js
│       └── custom-macd.js
└── frontend/src/dsl-ide/       # IDE源代码
```

### 本地存储配置
```typescript
// IDE配置存储
interface IDEConfig {
  theme: 'light' | 'dark';
  fontSize: number;
  autoSave: boolean;
  autoCompile: boolean;
  recentFiles: string[];
}

// 使用localStorage存储用户配置
const CONFIG_KEY = 'dsl-ide-config';
const saveConfig = (config: IDEConfig) => {
  localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
};
```

## 核心实现代码

### 1. DSL词法分析器实现

```typescript
// src/compiler/lexer.ts
export enum TokenType {
  // 关键字
  INDICATOR = 'INDICATOR',
  INPUT = 'INPUT',
  PLOT = 'PLOT',
  
  // 标识符和字面量
  IDENTIFIER = 'IDENTIFIER',
  NUMBER = 'NUMBER',
  STRING = 'STRING',
  COLOR = 'COLOR',
  BOOLEAN = 'BOOLEAN',
  
  // 操作符
  ASSIGN = 'ASSIGN',
  PLUS = 'PLUS',
  MINUS = 'MINUS',
  MULTIPLY = 'MULTIPLY',
  DIVIDE = 'DIVIDE',
  
  // 分隔符
  LPAREN = 'LPAREN',
  RPAREN = 'RPAREN',
  COMMA = 'COMMA',
  
  // 特殊
  EOF = 'EOF',
  NEWLINE = 'NEWLINE'
}

export interface Token {
  type: TokenType;
  value: string;
  line: number;
  column: number;
}

export class Lexer {
  private source: string;
  private position: number = 0;
  private line: number = 1;
  private column: number = 1;
  
  constructor(source: string) {
    this.source = source;
  }
  
  tokenize(): Token[] {
    const tokens: Token[] = [];
    
    while (this.position < this.source.length) {
      const token = this.nextToken();
      if (token) {
        tokens.push(token);
      }
    }
    
    tokens.push({
      type: TokenType.EOF,
      value: '',
      line: this.line,
      column: this.column
    });
    
    return tokens;
  }
  
  private nextToken(): Token | null {
    this.skipWhitespace();
    
    if (this.position >= this.source.length) {
      return null;
    }
    
    const char = this.source[this.position];
    const line = this.line;
    const column = this.column;
    
    // 数字
    if (/\d/.test(char)) {
      return this.readNumber(line, column);
    }
    
    // 字符串
    if (char === '"' || char === "'") {
      return this.readString(line, column);
    }
    
    // 颜色值
    if (char === '#') {
      return this.readColor(line, column);
    }
    
    // 标识符和关键字
    if (/[a-zA-Z_]/.test(char)) {
      return this.readIdentifier(line, column);
    }
    
    // 单字符token
    switch (char) {
      case '=':
        this.advance();
        return { type: TokenType.ASSIGN, value: '=', line, column };
      case '+':
        this.advance();
        return { type: TokenType.PLUS, value: '+', line, column };
      case '-':
        this.advance();
        return { type: TokenType.MINUS, value: '-', line, column };
      case '*':
        this.advance();
        return { type: TokenType.MULTIPLY, value: '*', line, column };
      case '/':
        this.advance();
        return { type: TokenType.DIVIDE, value: '/', line, column };
      case '(':
        this.advance();
        return { type: TokenType.LPAREN, value: '(', line, column };
      case ')':
        this.advance();
        return { type: TokenType.RPAREN, value: ')', line, column };
      case ',':
        this.advance();
        return { type: TokenType.COMMA, value: ',', line, column };
      case '\n':
        this.advance();
        return { type: TokenType.NEWLINE, value: '\n', line, column };
    }
    
    throw new Error(`Unexpected character: ${char} at line ${line}, column ${column}`);
  }
  
  private readNumber(line: number, column: number): Token {
    let value = '';
    
    while (this.position < this.source.length && /[\d.]/.test(this.source[this.position])) {
      value += this.source[this.position];
      this.advance();
    }
    
    return { type: TokenType.NUMBER, value, line, column };
  }
  
  private readString(line: number, column: number): Token {
    const quote = this.source[this.position];
    this.advance(); // 跳过开始引号
    
    let value = '';
    while (this.position < this.source.length && this.source[this.position] !== quote) {
      value += this.source[this.position];
      this.advance();
    }
    
    if (this.position >= this.source.length) {
      throw new Error(`Unterminated string at line ${line}, column ${column}`);
    }
    
    this.advance(); // 跳过结束引号
    return { type: TokenType.STRING, value, line, column };
  }
  
  private readColor(line: number, column: number): Token {
    let value = '#';
    this.advance(); // 跳过#
    
    while (this.position < this.source.length && /[0-9A-Fa-f]/.test(this.source[this.position])) {
      value += this.source[this.position];
      this.advance();
    }
    
    if (value.length !== 7) {
      throw new Error(`Invalid color format at line ${line}, column ${column}`);
    }
    
    return { type: TokenType.COLOR, value, line, column };
  }
  
  private readIdentifier(line: number, column: number): Token {
    let value = '';
    
    while (this.position < this.source.length && /[a-zA-Z0-9_]/.test(this.source[this.position])) {
      value += this.source[this.position];
      this.advance();
    }
    
    // 检查是否为关键字
    const keywords: Record<string, TokenType> = {
      'indicator': TokenType.INDICATOR,
      'input': TokenType.INPUT,
      'plot': TokenType.PLOT,
      'true': TokenType.BOOLEAN,
      'false': TokenType.BOOLEAN
    };
    
    const type = keywords[value] || TokenType.IDENTIFIER;
    return { type, value, line, column };
  }
  
  private skipWhitespace(): void {
    while (this.position < this.source.length) {
      const char = this.source[this.position];
      if (char === ' ' || char === '\t' || char === '\r') {
        this.advance();
      } else if (char === '/' && this.source[this.position + 1] === '/') {
        // 跳过单行注释
        while (this.position < this.source.length && this.source[this.position] !== '\n') {
          this.advance();
        }
      } else {
        break;
      }
    }
  }
  
  private advance(): void {
    if (this.position < this.source.length) {
      if (this.source[this.position] === '\n') {
        this.line++;
        this.column = 1;
      } else {
        this.column++;
      }
      this.position++;
    }
  }
}
```

### 2. AST节点定义

```typescript
// src/compiler/ast.ts
export interface ASTNode {
  type: string;
  line: number;
  column: number;
}

export interface ProgramNode extends ASTNode {
  type: 'Program';
  indicator: IndicatorNode;
  inputs: InputNode[];
  variables: VariableNode[];
  plots: PlotNode[];
}

export interface IndicatorNode extends ASTNode {
  type: 'Indicator';
  name: string;
  shortName: string;
  properties: PropertyNode[];
}

export interface PropertyNode extends ASTNode {
  type: 'Property';
  key: string;
  value: ExpressionNode;
}

export interface InputNode extends ASTNode {
  type: 'Input';
  identifier: string;
  defaultValue: ExpressionNode;
  title?: string;
  properties: PropertyNode[];
}

export interface VariableNode extends ASTNode {
  type: 'Variable';
  identifier: string;
  expression: ExpressionNode;
}

export interface PlotNode extends ASTNode {
  type: 'Plot';
  expression: ExpressionNode;
  title?: string;
  color?: ExpressionNode;
  style?: ExpressionNode;
}

export interface ExpressionNode extends ASTNode {
  // 基类，具体表达式类型继承此接口
}

export interface BinaryExpressionNode extends ExpressionNode {
  type: 'BinaryExpression';
  left: ExpressionNode;
  operator: string;
  right: ExpressionNode;
}

export interface FunctionCallNode extends ExpressionNode {
  type: 'FunctionCall';
  name: string;
  arguments: ExpressionNode[];
}

export interface LiteralNode extends ExpressionNode {
  type: 'Literal';
  value: string | number | boolean;
  dataType: 'string' | 'number' | 'boolean' | 'color';
}

export interface IdentifierNode extends ExpressionNode {
  type: 'Identifier';
  name: string;
}
```

### 3. 语法分析器实现

```typescript
// src/compiler/parser.ts
import { Token, TokenType } from './lexer';
import * as AST from './ast';

export class Parser {
  private tokens: Token[];
  private current: number = 0;
  
  constructor(tokens: Token[]) {
    this.tokens = tokens;
  }
  
  parse(): AST.ProgramNode {
    const indicator = this.parseIndicator();
    const inputs: AST.InputNode[] = [];
    const variables: AST.VariableNode[] = [];
    const plots: AST.PlotNode[] = [];
    
    while (!this.isAtEnd()) {
      if (this.check(TokenType.IDENTIFIER) && this.peek().value === 'input') {
        // 这是一个input声明
        this.advance(); // 跳过identifier
        inputs.push(this.parseInput());
      } else if (this.check(TokenType.PLOT)) {
        plots.push(this.parsePlot());
      } else if (this.check(TokenType.IDENTIFIER)) {
        variables.push(this.parseVariable());
      } else {
        this.advance(); // 跳过不认识的token
      }
    }
    
    return {
      type: 'Program',
      line: 1,
      column: 1,
      indicator,
      inputs,
      variables,
      plots
    };
  }
  
  private parseIndicator(): AST.IndicatorNode {
    this.consume(TokenType.INDICATOR, "Expected 'indicator'");
    this.consume(TokenType.LPAREN, "Expected '('");
    
    const nameToken = this.consume(TokenType.STRING, "Expected indicator name");
    this.consume(TokenType.COMMA, "Expected ','");
    const shortNameToken = this.consume(TokenType.STRING, "Expected short name");
    
    const properties: AST.PropertyNode[] = [];
    while (this.check(TokenType.COMMA)) {
      this.advance(); // 跳过逗号
      properties.push(this.parseProperty());
    }
    
    this.consume(TokenType.RPAREN, "Expected ')')");
    
    return {
      type: 'Indicator',
      line: nameToken.line,
      column: nameToken.column,
      name: nameToken.value,
      shortName: shortNameToken.value,
      properties
    };
  }
  
  private parseInput(): AST.InputNode {
    const identifierToken = this.previous(); // 获取之前的identifier
    this.consume(TokenType.ASSIGN, "Expected '='");
    this.consume(TokenType.INPUT, "Expected 'input'");
    this.consume(TokenType.LPAREN, "Expected '('");
    
    const defaultValue = this.parseExpression();
    
    let title: string | undefined;
    if (this.check(TokenType.COMMA)) {
      this.advance();
      const titleToken = this.consume(TokenType.STRING, "Expected title string");
      title = titleToken.value;
    }
    
    const properties: AST.PropertyNode[] = [];
    while (this.check(TokenType.COMMA)) {
      this.advance();
      properties.push(this.parseProperty());
    }
    
    this.consume(TokenType.RPAREN, "Expected ')')");
    
    return {
      type: 'Input',
      line: identifierToken.line,
      column: identifierToken.column,
      identifier: identifierToken.value,
      defaultValue,
      title,
      properties
    };
  }
  
  private parseVariable(): AST.VariableNode {
    const identifierToken = this.consume(TokenType.IDENTIFIER, "Expected variable name");
    this.consume(TokenType.ASSIGN, "Expected '='");
    const expression = this.parseExpression();
    
    return {
      type: 'Variable',
      line: identifierToken.line,
      column: identifierToken.column,
      identifier: identifierToken.value,
      expression
    };
  }
  
  private parsePlot(): AST.PlotNode {
    const plotToken = this.consume(TokenType.PLOT, "Expected 'plot'");
    this.consume(TokenType.LPAREN, "Expected '('");
    
    const expression = this.parseExpression();
    
    let title: string | undefined;
    let color: AST.ExpressionNode | undefined;
    
    while (this.check(TokenType.COMMA)) {
      this.advance();
      if (this.check(TokenType.STRING)) {
        title = this.advance().value;
      } else {
        color = this.parseExpression();
      }
    }
    
    this.consume(TokenType.RPAREN, "Expected ')')");
    
    return {
      type: 'Plot',
      line: plotToken.line,
      column: plotToken.column,
      expression,
      title,
      color
    };
  }
  
  private parseExpression(): AST.ExpressionNode {
    return this.parseAddition();
  }
  
  private parseAddition(): AST.ExpressionNode {
    let expr = this.parseMultiplication();
    
    while (this.match(TokenType.PLUS, TokenType.MINUS)) {
      const operator = this.previous().value;
      const right = this.parseMultiplication();
      expr = {
        type: 'BinaryExpression',
        line: expr.line,
        column: expr.column,
        left: expr,
        operator,
        right
      };
    }
    
    return expr;
  }
  
  private parseMultiplication(): AST.ExpressionNode {
    let expr = this.parsePrimary();
    
    while (this.match(TokenType.MULTIPLY, TokenType.DIVIDE)) {
      const operator = this.previous().value;
      const right = this.parsePrimary();
      expr = {
        type: 'BinaryExpression',
        line: expr.line,
        column: expr.column,
        left: expr,
        operator,
        right
      };
    }
    
    return expr;
  }
  
  private parsePrimary(): AST.ExpressionNode {
    if (this.match(TokenType.NUMBER)) {
      const token = this.previous();
      return {
        type: 'Literal',
        line: token.line,
        column: token.column,
        value: parseFloat(token.value),
        dataType: 'number'
      };
    }
    
    if (this.match(TokenType.STRING)) {
      const token = this.previous();
      return {
        type: 'Literal',
        line: token.line,
        column: token.column,
        value: token.value,
        dataType: 'string'
      };
    }
    
    if (this.match(TokenType.COLOR)) {
      const token = this.previous();
      return {
        type: 'Literal',
        line: token.line,
        column: token.column,
        value: token.value,
        dataType: 'color'
      };
    }
    
    if (this.match(TokenType.BOOLEAN)) {
      const token = this.previous();
      return {
        type: 'Literal',
        line: token.line,
        column: token.column,
        value: token.value === 'true',
        dataType: 'boolean'
      };
    }
    
    if (this.check(TokenType.IDENTIFIER)) {
      const token = this.advance();
      
      // 检查是否为函数调用
      if (this.check(TokenType.LPAREN)) {
        this.advance(); // 跳过(
        const args: AST.ExpressionNode[] = [];
        
        if (!this.check(TokenType.RPAREN)) {
          do {
            args.push(this.parseExpression());
          } while (this.match(TokenType.COMMA));
        }
        
        this.consume(TokenType.RPAREN, "Expected ')')");
        
        return {
          type: 'FunctionCall',
          line: token.line,
          column: token.column,
          name: token.value,
          arguments: args
        };
      }
      
      // 普通标识符
      return {
        type: 'Identifier',
        line: token.line,
        column: token.column,
        name: token.value
      };
    }
    
    if (this.match(TokenType.LPAREN)) {
      const expr = this.parseExpression();
      this.consume(TokenType.RPAREN, "Expected ')' after expression");
      return expr;
    }
    
    throw new Error(`Unexpected token: ${this.peek().value} at line ${this.peek().line}`);
  }
  
  private parseProperty(): AST.PropertyNode {
    const keyToken = this.consume(TokenType.IDENTIFIER, "Expected property name");
    this.consume(TokenType.ASSIGN, "Expected '='");
    const value = this.parseExpression();
    
    return {
      type: 'Property',
      line: keyToken.line,
      column: keyToken.column,
      key: keyToken.value,
      value
    };
  }
  
  // 辅助方法
  private match(...types: TokenType[]): boolean {
    for (const type of types) {
      if (this.check(type)) {
        this.advance();
        return true;
      }
    }
    return false;
  }
  
  private check(type: TokenType): boolean {
    if (this.isAtEnd()) return false;
    return this.peek().type === type;
  }
  
  private advance(): Token {
    if (!this.isAtEnd()) this.current++;
    return this.previous();
  }
  
  private isAtEnd(): boolean {
    return this.peek().type === TokenType.EOF;
  }
  
  private peek(): Token {
    return this.tokens[this.current];
  }
  
  private previous(): Token {
    return this.tokens[this.current - 1];
  }
  
  private consume(type: TokenType, message: string): Token {
    if (this.check(type)) return this.advance();
    
    const token = this.peek();
    throw new Error(`${message}. Got ${token.value} at line ${token.line}, column ${token.column}`);
  }
}
```

### 4. 代码生成器实现

```typescript
// src/compiler/generator.ts
import * as AST from './ast';
import { BuiltinFunctions } from './builtin-functions';

export class CodeGenerator {
  private ast: AST.ProgramNode;
  private builtins: BuiltinFunctions;
  
  constructor(ast: AST.ProgramNode) {
    this.ast = ast;
    this.builtins = new BuiltinFunctions();
  }
  
  generate(): string {
    const indicator = this.ast.indicator;
    const inputs = this.ast.inputs;
    const plots = this.ast.plots;
    
    // 生成指标对象
    const code = `/**
 * Generated by DSL Compiler
 * Indicator: ${indicator.name}
 */

export default {
  name: '${indicator.name}',
  shortName: '${indicator.shortName}',
  precision: ${this.getProperty(indicator.properties, 'precision', '2')},
  calcParams: [${this.generateCalcParams(inputs)}],
  plots: [${this.generatePlots(plots)}],
  
  regeneratePlots: function(params) {
    return this.plots.map((plot, index) => ({
      ...plot,
      color: params[index]?.color || plot.color
    }));
  },
  
  calc: function(dataList, indicator, params) {
    const result = [];
    const length = dataList.length;
    
    ${this.generateCalcFunction()}
    
    return result;
  }
};
`;
    
    return code;
  }
  
  private generateCalcParams(inputs: AST.InputNode[]): string {
    return inputs.map(input => {
      const defaultValue = this.evaluateExpression(input.defaultValue);
      return `{
      name: '${input.identifier}',
      title: '${input.title || input.identifier}',
      value: ${JSON.stringify(defaultValue)}
    }`;
    }).join(',\n    ');
  }
  
  private generatePlots(plots: AST.PlotNode[]): string {
    return plots.map((plot, index) => {
      const color = plot.color ? this.evaluateExpression(plot.color) : '#2196F3';
      return `{
      key: 'plot${index}',
      title: '${plot.title || `Plot ${index + 1}`}',
      type: 'line',
      color: '${color}'
    }`;
    }).join(',\n    ');
  }
  
  private generateCalcFunction(): string {
    let code = '';
    
    // 生成变量声明
    for (const variable of this.ast.variables) {
      code += `    const ${variable.identifier} = ${this.generateExpression(variable.expression)};\n`;
    }
    
    // 生成计算循环
    code += `\n    for (let i = 0; i < length; i++) {\n`;
    code += `      const kLineData = dataList[i];\n`;
    code += `      const plotData = {};\n\n`;
    
    // 生成plot计算
    this.ast.plots.forEach((plot, index) => {
      code += `      plotData.plot${index} = ${this.generateExpression(plot.expression)};\n`;
    });
    
    code += `\n      result.push(plotData);\n`;
    code += `    }\n`;
    
    return code;
  }
  
  private generateExpression(expr: AST.ExpressionNode): string {
    switch (expr.type) {
      case 'Literal':
        const literal = expr as AST.LiteralNode;
        return typeof literal.value === 'string' ? `'${literal.value}'` : String(literal.value);
        
      case 'Identifier':
        const identifier = expr as AST.IdentifierNode;
        // 检查是否为内置数据访问
        if (['close', 'open', 'high', 'low', 'volume'].includes(identifier.name)) {
          return `kLineData.${identifier.name}`;
        }
        return identifier.name;
        
      case 'BinaryExpression':
        const binary = expr as AST.BinaryExpressionNode;
        return `(${this.generateExpression(binary.left)} ${binary.operator} ${this.generateExpression(binary.right)})`;
        
      case 'FunctionCall':
        const funcCall = expr as AST.FunctionCallNode;
        return this.generateFunctionCall(funcCall);
        
      default:
        throw new Error(`Unknown expression type: ${expr.type}`);
    }
  }
  
  private generateFunctionCall(funcCall: AST.FunctionCallNode): string {
    const funcName = funcCall.name;
    const args = funcCall.arguments.map(arg => this.generateExpression(arg));
    
    // 检查是否为内置函数
    if (this.builtins.hasFunction(funcName)) {
      return this.builtins.generateCall(funcName, args);
    }
    
    // 普通函数调用
    return `${funcName}(${args.join(', ')})`;
  }
  
  private getProperty(properties: AST.PropertyNode[], key: string, defaultValue: string): string {
    const prop = properties.find(p => p.key === key);
    if (prop) {
      return this.evaluateExpression(prop.value).toString();
    }
    return defaultValue;
  }
  
  private evaluateExpression(expr: AST.ExpressionNode): any {
    switch (expr.type) {
      case 'Literal':
        return (expr as AST.LiteralNode).value;
      case 'Identifier':
        return (expr as AST.IdentifierNode).name;
      default:
        return null;
    }
  }
}
```

### 5. 内置函数库实现

```typescript
// src/compiler/builtin-functions.ts
export class BuiltinFunctions {
  private functions: Map<string, FunctionDefinition> = new Map();
  
  constructor() {
    this.initializeFunctions();
  }
  
  hasFunction(name: string): boolean {
    return this.functions.has(name);
  }
  
  generateCall(name: string, args: string[]): string {
    const func = this.functions.get(name);
    if (!func) {
      throw new Error(`Unknown function: ${name}`);
    }
    
    return func.generator(args);
  }
  
  getCompletions(): CompletionItem[] {
    return Array.from(this.functions.entries()).map(([name, def]) => ({
      label: name,
      kind: 'Function',
      detail: def.signature,
      documentation: def.description,
      insertText: `${name}(${def.parameters.map((p, i) => `\${${i + 1}:${p.name}}`).join(', ')})`,
      insertTextRules: 'InsertAsSnippet'
    }));
  }
  
  private initializeFunctions(): void {
    // 简单移动平均
    this.functions.set('sma', {
      signature: 'sma(source: number[], length: number): number[]',
      description: '计算简单移动平均线',
      parameters: [
        { name: 'source', type: 'number[]' },
        { name: 'length', type: 'number' }
      ],
      generator: (args) => `this.calculateSMA(dataList, ${args[1]}, i)`
    });
    
    // 指数移动平均
    this.functions.set('ema', {
      signature: 'ema(source: number[], length: number): number[]',
      description: '计算指数移动平均线',
      parameters: [
        { name: 'source', type: 'number[]' },
        { name: 'length', type: 'number' }
      ],
      generator: (args) => `this.calculateEMA(dataList, ${args[1]}, i)`
    });
    
    // RSI相对强弱指标
    this.functions.set('rsi', {
      signature: 'rsi(source: number[], length: number): number[]',
      description: '计算相对强弱指标',
      parameters: [
        { name: 'source', type: 'number[]' },
        { name: 'length', type: 'number' }
      ],
      generator: (args) => `this.calculateRSI(dataList, ${args[1]}, i)`
    });
    
    // MACD指标
    this.functions.set('macd', {
      signature: 'macd(source: number[], fast: number, slow: number, signal: number): object',
      description: '计算MACD指标',
      parameters: [
        { name: 'source', type: 'number[]' },
        { name: 'fast', type: 'number' },
        { name: 'slow', type: 'number' },
        { name: 'signal', type: 'number' }
      ],
      generator: (args) => `this.calculateMACD(dataList, ${args[1]}, ${args[2]}, ${args[3]}, i)`
    });
    
    // 数学函数
    this.functions.set('max', {
      signature: 'max(source: number[], length: number): number',
      description: '计算最大值',
      parameters: [
        { name: 'source', type: 'number[]' },
        { name: 'length', type: 'number' }
      ],
      generator: (args) => `this.calculateMax(dataList, ${args[1]}, i)`
    });
    
    this.functions.set('min', {
      signature: 'min(source: number[], length: number): number',
      description: '计算最小值',
      parameters: [
        { name: 'source', type: 'number[]' },
        { name: 'length', type: 'number' }
      ],
      generator: (args) => `this.calculateMin(dataList, ${args[1]}, i)`
    });
  }
}

interface FunctionDefinition {
  signature: string;
  description: string;
  parameters: Parameter[];
  generator: (args: string[]) => string;
}

interface Parameter {
  name: string;
  type: string;
}

interface CompletionItem {
  label: string;
  kind: string;
  detail: string;
  documentation: string;
  insertText: string;
  insertTextRules: string;
}
```

## 交互要求

### 用户操作流程
1. **打开IDE** → 显示欢迎界面和文件列表
2. **创建新指标** → 提供模板选择
3. **编写DSL代码** → 实时语法高亮和错误检查
4. **实时编译** → 显示编译结果或错误信息
5. **预览代码** → 查看生成的JS代码
6. **保存指标** → 生成.dsl和.js文件
7. **测试指标** → 在klinechart中验证

### 异常情况处理
1. **语法错误** → 在编辑器中标红显示，提供错误信息和修复建议
2. **语义错误** → 类型不匹配、未定义变量等，提供详细错误说明
3. **编译失败** → 显示错误日志，阻止文件保存
4. **文件保存失败** → 提示用户检查权限和磁盘空间
5. **函数不存在** → 提供相似函数建议

### 用户体验优化
1. **智能提示** → 输入时自动显示可用函数和参数
2. **代码模板** → 提供常用指标模板快速开始
3. **快捷键** → Ctrl+S保存，Ctrl+Enter编译，F1帮助
4. **主题切换** → 支持明暗主题
5. **字体调节** → 支持字体大小调整

## 部署方案

### 目标运行环境
- **操作系统**：Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **浏览器**：Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Node.js版本**：16.0+
- **内存要求**：最小4GB，推荐8GB

### 依赖安装
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 安装Monaco Editor
npm install monaco-editor @monaco-editor/loader

# 安装开发依赖
npm install -D @types/node typescript vite @vitejs/plugin-vue
```

### 开发环境配置
```bash
# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码格式化
npm run format

# ESLint检查
npm run lint
```

### 生产构建
```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

### Docker部署（可选）
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 使用nginx提供静态文件服务
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 环境变量说明
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_DSL_COMPILER_DEBUG=true
VITE_MONACO_EDITOR_CDN=https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0

# .env.production
VITE_API_BASE_URL=https://api.daotrader.com
VITE_DSL_COMPILER_DEBUG=false
VITE_MONACO_EDITOR_CDN=https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0
```

### 启动命令
```bash
# 开发模式
npm run dev

# 生产模式（需要先构建）
npm run build
npm run preview

# 使用PM2部署（Node.js服务器）
pm2 start ecosystem.config.js
```

### 集成到现有项目
1. **路由配置**：在Vue Router中添加DSL IDE路由
2. **菜单集成**：在主导航中添加"指标编辑器"入口
3. **权限控制**：根据用户角色控制IDE访问权限
4. **文件系统**：确保indicators目录的读写权限

---

**重要提示**：
1. 严格按照现有项目的代码规范和架构模式
2. 所有生成的JS代码必须与klinechart完全兼容
3. 优先实现MVP功能，后续迭代增强
4. 充分测试DSL编译器的正确性和稳定性
5. 提供详细的错误信息和用户友好的提示

**交付标准**：
- DSL编译器能正确解析示例语法
- IDE提供基本的编辑和编译功能
- 生成的JS代码能在klinechart中正常运行
- 代码质量通过ESLint和TypeScript检查
- 提供基本的用户文档和使用说明