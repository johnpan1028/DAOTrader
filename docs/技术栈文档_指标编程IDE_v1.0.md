# 技术栈文档 - 专用指标编程IDE v1.0

## 技术架构概览

### 系统架构
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DSL Editor    │───▶│   DSL Compiler   │───▶│  JS Generator   │
│  (Monaco Editor)│    │   (Parser+AST)   │    │ (klinechart格式)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Syntax Highlight│    │  Error Handling  │    │  Code Preview   │
│  Auto Complete  │    │  Type Checking   │    │  File Export    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 前端技术栈

### 核心框架
- **Vue 3.4+**：主框架，与现有项目保持一致
- **TypeScript 5.0+**：类型安全，提升开发效率
- **Vite 5.0+**：构建工具，快速开发和热更新

### UI组件库
- **Element Plus 2.4+**：UI组件库，提供基础组件
- **Monaco Editor 0.45+**：代码编辑器核心
- **@monaco-editor/loader**：Monaco Editor Vue集成

### 状态管理
- **Pinia 2.1+**：状态管理，存储DSL代码和编译状态
- **VueUse 10.0+**：组合式API工具库

## DSL编译器技术栈

### 词法分析器
- **自定义Lexer**：基于正则表达式的词法分析
- **Token类型定义**：关键字、标识符、数字、字符串、操作符

### 语法分析器
- **递归下降解析器**：手写解析器，灵活控制
- **AST节点类型**：
  - IndicatorNode：指标声明节点
  - InputNode：参数输入节点
  - ExpressionNode：表达式节点
  - PlotNode：绘图输出节点
  - FunctionCallNode：函数调用节点

### 语义分析
- **类型检查系统**：
  - 基础类型：number, string, color, boolean
  - 数组类型：number[], 时间序列数据
  - 函数签名验证
- **作用域管理**：变量声明和引用检查

### 代码生成器
- **模板引擎**：基于字符串模板生成JS代码
- **优化器**：简单的代码优化（常量折叠、死代码消除）

## DSL语言规范

### 语法定义（EBNF）
```ebnf
program = indicator_decl input_decl* variable_decl* plot_decl*

indicator_decl = "indicator" "(" string "," string ("," property)* ")"
property = "overlay" "=" boolean | "precision" "=" number

input_decl = identifier "=" "input" "(" expression ("," string)? ("," property)* ")"

variable_decl = identifier "=" expression

plot_decl = "plot" "(" expression ("," string)? ("," expression)* ")"

expression = binary_expr | unary_expr | primary_expr
binary_expr = expression binary_op expression
unary_expr = unary_op expression
primary_expr = number | string | color | identifier | function_call | "(" expression ")"

function_call = identifier "(" (expression ("," expression)*)? ")"
```

### 内置函数库
```typescript
interface BuiltinFunctions {
  // 移动平均类
  sma(source: number[], length: number): number[];
  ema(source: number[], length: number): number[];
  wma(source: number[], length: number): number[];
  
  // 技术指标类
  rsi(source: number[], length: number): number[];
  macd(source: number[], fast: number, slow: number, signal: number): {
    macd: number[], signal: number[], histogram: number[]
  };
  
  // 数学函数类
  max(source: number[], length: number): number[];
  min(source: number[], length: number): number[];
  sum(source: number[], length: number): number[];
  
  // 数据访问
  close: number[];
  open: number[];
  high: number[];
  low: number[];
  volume: number[];
}
```

## 编译器实现架构

### 核心类设计
```typescript
// 词法分析器
class Lexer {
  private source: string;
  private position: number;
  
  tokenize(): Token[];
  private nextToken(): Token;
  private skipWhitespace(): void;
}

// 语法分析器
class Parser {
  private tokens: Token[];
  private current: number;
  
  parse(): ProgramNode;
  private parseIndicator(): IndicatorNode;
  private parseExpression(): ExpressionNode;
}

// 代码生成器
class CodeGenerator {
  private ast: ProgramNode;
  
  generate(): string;
  private generateIndicatorObject(): string;
  private generateCalcFunction(): string;
}

// 编译器主类
class DSLCompiler {
  compile(source: string): CompileResult;
  private validate(ast: ProgramNode): ValidationResult;
}
```

### 错误处理系统
```typescript
interface CompileError {
  type: 'lexical' | 'syntax' | 'semantic';
  message: string;
  line: number;
  column: number;
  suggestion?: string;
}

interface CompileResult {
  success: boolean;
  code?: string;
  errors: CompileError[];
  warnings: CompileError[];
}
```

## IDE编辑器技术实现

### Monaco Editor配置
```typescript
// 语言注册
monaco.languages.register({ id: 'dsl-indicator' });

// 语法高亮
monaco.languages.setMonarchTokensProvider('dsl-indicator', {
  tokenizer: {
    root: [
      [/\b(indicator|input|plot)\b/, 'keyword'],
      [/\b(sma|ema|rsi|macd)\b/, 'function'],
      [/\b(close|open|high|low|volume)\b/, 'variable.predefined'],
      [/#[0-9A-Fa-f]{6}/, 'number.hex'],
      [/\d+(\.\d+)?/, 'number'],
      [/".*?"/, 'string'],
    ]
  }
});

// 自动补全
monaco.languages.registerCompletionItemProvider('dsl-indicator', {
  provideCompletionItems: (model, position) => {
    return {
      suggestions: [
        {
          label: 'sma',
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: 'sma(${1:source}, ${2:length})',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet
        }
      ]
    };
  }
});
```

### 实时编译集成
```typescript
class IDEController {
  private editor: monaco.editor.IStandaloneCodeEditor;
  private compiler: DSLCompiler;
  
  setupRealTimeCompilation() {
    this.editor.onDidChangeModelContent(() => {
      debounce(() => {
        const source = this.editor.getValue();
        const result = this.compiler.compile(source);
        this.updateErrorMarkers(result.errors);
        this.updatePreview(result.code);
      }, 500)();
    });
  }
}
```

## 项目结构

```
frontend/src/
├── components/
│   ├── DSLEditor/
│   │   ├── DSLEditor.vue          # 主编辑器组件
│   │   ├── ErrorPanel.vue         # 错误显示面板
│   │   ├── PreviewPanel.vue       # 代码预览面板
│   │   └── FunctionHelper.vue     # 函数帮助面板
│   └── common/
├── compiler/
│   ├── lexer.ts                   # 词法分析器
│   ├── parser.ts                  # 语法分析器
│   ├── ast.ts                     # AST节点定义
│   ├── generator.ts               # 代码生成器
│   ├── builtin-functions.ts       # 内置函数定义
│   └── index.ts                   # 编译器入口
├── stores/
│   ├── dsl-editor.ts              # DSL编辑器状态
│   └── compiler.ts                # 编译器状态
├── types/
│   ├── dsl.ts                     # DSL类型定义
│   └── compiler.ts                # 编译器类型定义
└── views/
    └── DSLIdeView.vue             # IDE主界面
```

## 依赖管理

### package.json核心依赖
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "@monaco-editor/loader": "^1.4.0",
    "monaco-editor": "^0.45.0",
    "element-plus": "^2.4.0",
    "pinia": "^2.1.0",
    "@vueuse/core": "^10.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^5.0.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  }
}
```

## 构建和部署

### 开发环境
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 类型检查
npm run type-check

# 代码格式化
npm run format
```

### 生产构建
```bash
# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

### 集成到现有项目
1. 在现有Vue项目中添加DSL编辑器路由
2. 编译器作为独立模块，可在Node.js环境中运行
3. 生成的JS文件直接保存到indicators目录

## 性能优化策略

### 编译器优化
- **增量编译**：只重新编译修改的部分
- **缓存机制**：缓存AST和编译结果
- **Web Worker**：在后台线程执行编译

### 编辑器优化
- **虚拟滚动**：处理大文件时的性能优化
- **防抖处理**：减少实时编译频率
- **懒加载**：按需加载Monaco Editor功能

## 测试策略

### 单元测试
- **Lexer测试**：词法分析正确性
- **Parser测试**：语法分析和AST生成
- **Generator测试**：代码生成正确性
- **函数库测试**：内置函数计算准确性

### 集成测试
- **端到端编译**：DSL到JS的完整流程
- **klinechart兼容性**：生成代码的实际运行测试
- **IDE功能测试**：编辑器交互功能

### 测试工具
- **Vitest**：单元测试框架
- **Playwright**：端到端测试
- **Jest**：编译器核心逻辑测试

---

**文档版本**：v1.0  
**创建日期**：2024年1月  
**最后更新**：2024年1月  
**技术负责人**：开发团队