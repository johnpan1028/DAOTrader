<template>
  <div class="indicator-ide">
    <!-- 顶部工具栏 -->
    <div class="ide-toolbar">
      <div class="toolbar-left">

        
        <el-button-group>
          <el-tooltip content="新建指标文件">
            <el-button :icon="DocumentAdd" @click="createNewFile" size="small">新建</el-button>
          </el-tooltip>
          <el-tooltip content="复制选中文件">
            <el-button :icon="CopyDocument" @click="copyFile" size="small" :disabled="!activeEditorTab">复制</el-button>
          </el-tooltip>
          <el-tooltip content="删除选中文件">
            <el-button :icon="Delete" @click="deleteFile" size="small" :disabled="!selectedFileNode">删除</el-button>
          </el-tooltip>
          <el-tooltip content="重命名选中文件">
            <el-button :icon="Edit" @click="renameFile" size="small" :disabled="!selectedFileNode">重命名</el-button>
          </el-tooltip>
        </el-button-group>
        
        <el-divider direction="vertical" />
        
        <el-select 
          v-model="selectedTemplate" 
          placeholder="选择模板"
          @change="loadTemplate"
          size="small"
          style="width: 150px"
        >
          <el-option 
            v-for="template in templates" 
            :key="template.value" 
            :label="template.label" 
            :value="template.value"
          />
        </el-select>
      </div>
      
      <div class="toolbar-right">
        <el-tooltip content="格式化代码">
          <el-button 
            :icon="MagicStick" 
            size="small" 
            @click="formatCode"
          />
        </el-tooltip>
        <el-tooltip content="全屏编辑">
          <el-button 
            :icon="FullScreen" 
            size="small" 
            @click="toggleFullscreen"
          />
        </el-tooltip>
      </div>
    </div>
    
    <!-- T型布局主体 -->
    <div class="ide-main">
      <!-- 左侧文件树 -->
      <div class="file-tree-panel">
        <div class="panel-header">
          <span>指标文件</span>
          <div class="header-actions">
            <el-tooltip content="刷新">
              <el-button 
                :icon="Refresh" 
                size="small" 
                @click="refreshFileTree"
              />
            </el-tooltip>
          </div>
        </div>
        
        <div class="file-tree-content">
          <el-tree
            :data="fileTreeData"
            :props="treeProps"
            @node-click="handleFileSelect"
            :highlight-current="true"
            node-key="id"
            draggable
            :allow-drop="allowDrop"
            :allow-drag="allowDrag"
            @node-drop="handleNodeDrop"
          >
            <template #default="{ node, data }">
              <span class="file-tree-node">
                <el-icon v-if="data.type === 'folder'"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
                <span class="node-label">{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </div>
      </div>
      
      <!-- 右侧IDE区域 -->
      <div class="ide-right-panel">
        <!-- 编辑器区域 -->
        <div class="editor-section">
          <div class="editor-tabs">
            <el-tabs 
              v-model="activeEditorTab" 
              type="card" 
              closable
              @tab-remove="closeTab"
            >
              <el-tab-pane 
                v-for="tab in editorTabs" 
                :key="tab.id" 
                :label="tab.name" 
                :name="tab.id"
              >
                <div class="tab-editor-container" :data-tab-id="tab.id">
                  <!-- Monaco Editor 将在这里挂载 -->
                </div>
              </el-tab-pane>
            </el-tabs>
            
            <!-- 默认欢迎页面 -->
            <div v-if="editorTabs.length === 0" class="welcome-panel">
              <div class="welcome-content">
                <h3>欢迎使用指标编程IDE</h3>
                <p>请从左侧文件树选择文件开始编辑，或创建新的指标文件。</p>
                <el-button type="primary" @click="newIndicator">创建新指标</el-button>
              </div>
            </div>
          </div>
          
          <!-- 编译结果面板 -->
          <div class="compile-result" v-if="compiledResult">
            <div class="result-header">
              <span :class="['result-status', compiledResult.success ? 'success' : 'error']">
                <el-icon><Check v-if="compiledResult.success" /><Close v-else /></el-icon>
                {{ compiledResult.success ? '编译成功' : '编译失败' }}
              </span>
            </div>
            
            <div class="result-content" v-if="!compiledResult.success">
              <pre class="error-message">{{ compiledResult.error }}</pre>
            </div>
            
            <div class="result-content" v-else>
              <el-tabs v-model="activeResultTab">
                <el-tab-pane label="JavaScript" name="js">
                  <pre class="code-output">{{ compiledResult.jsCode }}</pre>
                </el-tab-pane>
                <el-tab-pane label="VNPY格式" name="vnpy">
                  <pre class="code-output">{{ JSON.stringify(compiledResult.vnpyIndicator, null, 2) }}</pre>
                </el-tab-pane>
                <el-tab-pane label="KLineChart格式" name="kline">
                  <pre class="code-output">{{ JSON.stringify(compiledResult.klineIndicator, null, 2) }}</pre>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </div>
        
        <!-- AI助手输入条 -->
        <div class="ai-input-panel">
          <div class="ai-input-header">
            <span>AI助手</span>
            <el-button 
              :icon="ChatDotRound" 
              size="small" 
              @click="toggleAIPanel"
              :type="showAIPanel ? 'primary' : 'default'"
            >
              {{ showAIPanel ? '收起' : '展开' }}
            </el-button>
          </div>
          
          <!-- AI聊天面板 -->
          <div class="ai-chat-panel" v-show="showAIPanel">
            <div class="chat-messages" ref="chatMessagesContainer">
              <div 
                v-for="(message, index) in chatMessages" 
                :key="index" 
                :class="['message', message.type]"
              >
                <div class="message-content">
                  {{ message.content }}
                </div>
                <div class="message-time">
                  {{ formatTime(message.timestamp) }}
                </div>
              </div>
            </div>
            
            <div class="chat-input">
              <el-input 
                v-model="chatInput" 
                type="textarea" 
                :rows="2" 
                placeholder="描述你想要的指标，例如：创建一个双均线交叉指标，快线周期5，慢线周期20"
                @keydown.ctrl.enter="sendMessage"
              />
              <div class="input-actions">
                <el-button 
                  type="primary" 
                  size="small"
                  @click="sendMessage"
                  :loading="aiProcessing"
                >
                  发送 (Ctrl+Enter)
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- AI对话框 -->
    <el-dialog 
      v-model="showAIDialog" 
      title="AI指标助手" 
      width="600px"
      :before-close="handleAIDialogClose"
    >
      <div class="ai-chat">
        <div class="chat-messages" ref="chatMessagesContainer">
          <div 
            v-for="(message, index) in chatMessages" 
            :key="index" 
            :class="['message', message.type]"
          >
            <div class="message-content">
              {{ message.content }}
            </div>
            <div class="message-time">
              {{ formatTime(message.timestamp) }}
            </div>
          </div>
        </div>
        
        <div class="chat-input">
          <el-input 
            v-model="chatInput" 
            type="textarea" 
            :rows="3" 
            placeholder="描述你想要的指标，例如：创建一个双均线交叉指标，快线周期5，慢线周期20"
            @keydown.ctrl.enter="sendMessage"
          />
          <div class="input-actions">
            <el-button 
              type="primary" 
              @click="sendMessage"
              :loading="aiProcessing"
            >
              发送 (Ctrl+Enter)
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
    
    <!-- 保存对话框 -->
    <el-dialog v-model="showSaveDialog" title="保存指标" width="400px">
      <el-form :model="saveForm" label-width="80px">
        <el-form-item label="指标名称">
          <el-input v-model="saveForm.name" placeholder="请输入指标名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="saveForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入指标描述"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="saveForm.category" placeholder="选择分类">
            <el-option label="趋势指标" value="trend" />
            <el-option label="震荡指标" value="oscillator" />
            <el-option label="成交量指标" value="volume" />
            <el-option label="自定义指标" value="custom" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSaveDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmSave">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 加载对话框 -->
    <el-dialog v-model="showLoadDialog" title="加载指标" width="600px">
      <el-table 
        :data="savedIndicators" 
        @row-click="selectIndicator"
        highlight-current-row
      >
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="updateTime" label="更新时间" width="180" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button 
              type="danger" 
              size="small" 
              @click.stop="deleteIndicator(row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="showLoadDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmLoad"
          :disabled="!selectedIndicatorId"
        >
          加载
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  CaretRight,
  VideoPlay,
  Download,
  FolderOpened,
  DocumentAdd,
  ChatDotRound,
  MagicStick,
  FullScreen,
  Close,
  Check,
  Refresh,
  Folder,
  Document,
  CopyDocument,
  Delete,
  Edit
} from '@element-plus/icons-vue'
import * as monaco from 'monaco-editor'
import { maiLangCompiler } from '@/utils/maiLangCompiler'
import { init as initKLineChart, dispose as disposeKLineChart } from 'klinecharts'

// 响应式数据
const editorContainer = ref(null)
const chartContainer = ref(null)
const chatMessagesContainer = ref(null)

// 文件树相关
const fileTreeData = ref([
  {
    id: 'indicators',
    label: '指标文件',
    type: 'folder',
    children: [
      { id: 'trend', label: '趋势指标', type: 'folder', children: [
        { id: 'dual_ma', label: '双均线.mai', type: 'file' },
        { id: 'macd', label: 'MACD.mai', type: 'file' }
      ]},
      { id: 'oscillator', label: '震荡指标', type: 'folder', children: [
        { id: 'rsi', label: 'RSI.mai', type: 'file' },
        { id: 'kdj', label: 'KDJ.mai', type: 'file' }
      ]},
      { id: 'volume', label: '成交量指标', type: 'folder', children: [
        { id: 'boll', label: '布林带.mai', type: 'file' }
      ]},
      { id: 'custom', label: '自定义指标', type: 'folder', children: [] }
    ]
  }
])
const treeProps = {
  children: 'children',
  label: 'label'
}

// 编辑器标签页
const editorTabs = ref([])
const activeEditorTab = ref('')
const editorRefs = ref(new Map())

const compiling = ref(false)
const showPreview = ref(false)
const showAIDialog = ref(false)
const showSaveDialog = ref(false)
const showLoadDialog = ref(false)
const aiProcessing = ref(false)
const showAIPanel = ref(false)

const selectedTemplate = ref('')
const activeResultTab = ref('js')
const chatInput = ref('')
const selectedIndicatorId = ref(null)
const selectedFileNode = ref(null)

// 编辑器和图表实例
let editor = null
let chart = null

// 编译结果
const compiledResult = ref(null)

// 聊天消息
const chatMessages = ref([
  {
    type: 'assistant',
    content: '你好！我是AI指标助手，可以帮你生成麦语言指标代码。请描述你想要的指标功能。',
    timestamp: Date.now()
  }
])

// 保存表单
const saveForm = ref({
  name: '',
  description: '',
  category: ''
})

// 已保存的指标
const savedIndicators = ref([])

// 模板列表
const templates = ref([
  { label: '双均线', value: 'dual_ma' },
  { label: 'MACD', value: 'macd' },
  { label: 'RSI', value: 'rsi' },
  { label: 'KDJ', value: 'kdj' },
  { label: '布林带', value: 'boll' },
  { label: '自定义', value: 'custom' }
])

// 模板代码
const templateCodes = {
  dual_ma: `// 双均线指标
// 参数定义
parameter MA1_PERIOD = 5;    // 短期均线周期
parameter MA2_PERIOD = 20;   // 长期均线周期

// 计算均线
MA1 = MA(CLOSE, MA1_PERIOD);
MA2 = MA(CLOSE, MA2_PERIOD);

// 输出线条
DRAWLINE(MA1, COLOR_YELLOW, "短期均线");
DRAWLINE(MA2, COLOR_BLUE, "长期均线");

// 交易信号
if (CROSS(MA1, MA2)) {
    DRAWICON(LOW, ICON_UP, "金叉买入");
}
if (CROSS(MA2, MA1)) {
    DRAWICON(HIGH, ICON_DOWN, "死叉卖出");
}`,
  
  macd: `// MACD指标
// 参数定义
parameter FAST_PERIOD = 12;  // 快线周期
parameter SLOW_PERIOD = 26;  // 慢线周期
parameter SIGNAL_PERIOD = 9; // 信号线周期

// 计算MACD
DIF = EMA(CLOSE, FAST_PERIOD) - EMA(CLOSE, SLOW_PERIOD);
DEA = EMA(DIF, SIGNAL_PERIOD);
MACD_HIST = (DIF - DEA) * 2;

// 输出线条
DRAWLINE(DIF, COLOR_BLUE, "DIF");
DRAWLINE(DEA, COLOR_YELLOW, "DEA");
DRAWHIST(MACD_HIST, COLOR_RED, COLOR_GREEN, "MACD柱");

// 零轴线
DRAWLINE(0, COLOR_GRAY, "零轴");`,
  
  rsi: `// RSI指标
// 参数定义
parameter RSI_PERIOD = 14;   // RSI周期
parameter OVERBOUGHT = 70;   // 超买线
parameter OVERSOLD = 30;     // 超卖线

// 计算RSI
RSI_VALUE = RSI(CLOSE, RSI_PERIOD);

// 输出线条
DRAWLINE(RSI_VALUE, COLOR_BLUE, "RSI");
DRAWLINE(OVERBOUGHT, COLOR_RED, "超买线");
DRAWLINE(OVERSOLD, COLOR_GREEN, "超卖线");

// 背景色
if (RSI_VALUE > OVERBOUGHT) {
    DRAWBAND(RSI_VALUE, OVERBOUGHT, COLOR_RED_ALPHA);
}
if (RSI_VALUE < OVERSOLD) {
    DRAWBAND(OVERSOLD, RSI_VALUE, COLOR_GREEN_ALPHA);
}`,
  
  kdj: `// KDJ指标
// 参数定义
parameter KDJ_PERIOD = 9;    // KDJ周期
parameter K_SMOOTH = 3;      // K值平滑
parameter D_SMOOTH = 3;      // D值平滑

// 计算KDJ
RSV = (CLOSE - LLV(LOW, KDJ_PERIOD)) / (HHV(HIGH, KDJ_PERIOD) - LLV(LOW, KDJ_PERIOD)) * 100;
K = SMA(RSV, K_SMOOTH, 1);
D = SMA(K, D_SMOOTH, 1);
J = 3 * K - 2 * D;

// 输出线条
DRAWLINE(K, COLOR_BLUE, "K线");
DRAWLINE(D, COLOR_YELLOW, "D线");
DRAWLINE(J, COLOR_MAGENTA, "J线");

// 参考线
DRAWLINE(80, COLOR_RED, "超买线");
DRAWLINE(20, COLOR_GREEN, "超卖线");
DRAWLINE(50, COLOR_GRAY, "中轴线");`,
  
  boll: `// 布林带指标
// 参数定义
parameter BOLL_PERIOD = 20;  // 布林带周期
parameter STD_DEV = 2;       // 标准差倍数

// 计算布林带
MID = MA(CLOSE, BOLL_PERIOD);
STD = STDEV(CLOSE, BOLL_PERIOD);
UPPER = MID + STD * STD_DEV;
LOWER = MID - STD * STD_DEV;

// 输出线条
DRAWLINE(UPPER, COLOR_RED, "上轨");
DRAWLINE(MID, COLOR_YELLOW, "中轨");
DRAWLINE(LOWER, COLOR_GREEN, "下轨");

// 填充区域
DRAWBAND(UPPER, LOWER, COLOR_BLUE_ALPHA, "布林带通道");

// 交易信号
if (CROSS(CLOSE, UPPER)) {
    DRAWICON(HIGH, ICON_DOWN, "突破上轨");
}
if (CROSS(LOWER, CLOSE)) {
    DRAWICON(LOW, ICON_UP, "突破下轨");
}`,
  
  custom: `// 自定义指标模板
// 在这里编写您的指标代码

// 参数定义示例
// parameter PERIOD = 20;

// 计算示例
// VALUE = MA(CLOSE, PERIOD);

// 输出示例
// DRAWLINE(VALUE, COLOR_BLUE, "指标线");

// 开始编写您的代码...`
}

// 组件挂载
onMounted(async () => {
  await initEditor()
  loadSavedIndicators()
})

// 组件卸载
onUnmounted(() => {
  if (editor) {
    editor.dispose()
  }
  if (chart) {
    disposeKLineChart(chart)
  }
})

// 初始化编辑器
async function initEditor() {
  // 注册麦语言
  monaco.languages.register({ id: 'mailang' })
  
  // 设置语法高亮
  monaco.languages.setMonarchTokensProvider('mailang', {
    tokenizer: {
      root: [
        // 注释
        [/\/\/.*$/, 'comment'],
        
        // 关键字
        [/\b(IF|THEN|ELSE|AND|OR|NOT|TRUE|FALSE)\b/, 'keyword'],
        
        // 函数
        [/\b(MA|EMA|SMA|WMA|RSI|MACD|KDJ|BOLL|ATR|CCI|WR|BIAS|PSY|DMI|REF|SUM|STD|HHV|LLV|COUNT|EVERY|EXIST|CROSS|BARSLAST|ABS|MAX|MIN|SQRT|POW|LN|SIN|COS|TAN)\b/, 'function'],
        
        // 内置变量
        [/\b(OPEN|HIGH|LOW|CLOSE|VOL|VOLUME|O|H|L|C|V)\b/, 'variable.predefined'],
        
        // 颜色关键字
        [/\b(COLOR\w+|STICK|LINETHICK\d+)\b/, 'type'],
        
        // 数字
        [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
        [/\d+/, 'number'],
        
        // 字符串
        [/"([^"\\]|\\.)*$/, 'string.invalid'],
        [/"/, 'string', '@string'],
        
        // 操作符
        [/:=/, 'operator.assignment'],
        [/[=!<>]=?/, 'operator.comparison'],
        [/[+\-*/]/, 'operator.arithmetic'],
        [/[()\[\]{}]/, 'delimiter.bracket'],
        [/[,;]/, 'delimiter'],
        
        // 标识符
        [/[a-zA-Z_]\w*/, 'identifier']
      ],
      
      string: [
        [/[^\\"]+/, 'string'],
        [/\\./, 'string.escape.invalid'],
        [/"/, 'string', '@pop']
      ]
    }
  })
  
  // 设置主题
  monaco.editor.defineTheme('mailang-theme', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6A9955' },
      { token: 'keyword', foreground: 'C586C0' },
      { token: 'function', foreground: 'DCDCAA' },
      { token: 'variable.predefined', foreground: '4FC1FF' },
      { token: 'type', foreground: '4EC9B0' },
      { token: 'number', foreground: 'B5CEA8' },
      { token: 'string', foreground: 'CE9178' },
      { token: 'operator', foreground: 'D4D4D4' },
      { token: 'identifier', foreground: '9CDCFE' }
    ],
    colors: {
      'editor.background': '#1E1E1E'
    }
  })
  
  // 设置自动完成
  monaco.languages.registerCompletionItemProvider('mailang', {
    provideCompletionItems: (model, position) => {
      const suggestions = [
        // 函数建议
        ...[
          'MA', 'EMA', 'SMA', 'WMA', 'RSI', 'MACD', 'KDJ', 'BOLL', 'ATR', 'CCI', 'WR', 'BIAS', 'PSY', 'DMI',
          'REF', 'SUM', 'STD', 'HHV', 'LLV', 'COUNT', 'EVERY', 'EXIST', 'CROSS', 'BARSLAST',
          'ABS', 'MAX', 'MIN', 'SQRT', 'POW', 'LN', 'SIN', 'COS', 'TAN'
        ].map(func => ({
          label: func,
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: `${func}($1)`,
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: `${func}函数`
        })),
        
        // 变量建议
        ...[
          'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOL', 'VOLUME', 'O', 'H', 'L', 'C', 'V'
        ].map(variable => ({
          label: variable,
          kind: monaco.languages.CompletionItemKind.Variable,
          insertText: variable,
          documentation: `内置变量: ${variable}`
        })),
        
        // 关键字建议
        ...[
          'IF', 'THEN', 'ELSE', 'AND', 'OR', 'NOT', 'TRUE', 'FALSE'
        ].map(keyword => ({
          label: keyword,
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: keyword
        }))
      ]
      
      return { suggestions }
    }
  })
  
  // 创建编辑器
  editor = monaco.editor.create(editorContainer.value, {
    value: templateCodes.custom,
    language: 'mailang',
    theme: 'mailang-theme',
    fontSize: 14,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    wordWrap: 'on',
    lineNumbers: 'on',
    glyphMargin: true,
    folding: true,
    lineDecorationsWidth: 10,
    lineNumbersMinChars: 3
  })
  
  // 监听内容变化
  editor.onDidChangeModelContent(() => {
    // 清除之前的编译结果
    compiledResult.value = null
  })
}

// 编译代码
function compileCode() {
  if (!editor) return
  
  compiling.value = true
  const code = editor.getValue()
  
  try {
    const result = maiLangCompiler.compile(code)
    compiledResult.value = result
    
    if (result.success) {
      ElMessage.success('编译成功！')
    } else {
      ElMessage.error(`编译失败: ${result.error}`)
    }
  } catch (error) {
    ElMessage.error(`编译器错误: ${error.message}`)
    compiledResult.value = {
      success: false,
      error: error.message
    }
  } finally {
    compiling.value = false
  }
}

// 预览指标
function previewIndicator() {
  if (!compiledResult.value?.success) {
    ElMessage.warning('请先编译成功后再预览')
    return
  }
  
  showPreview.value = true
  
  nextTick(() => {
    initChart()
  })
}

// 初始化图表
function initChart() {
  if (!chartContainer.value) return
  
  // 销毁现有图表
  if (chart) {
    disposeKLineChart(chart)
  }
  
  // 创建新图表
  chart = initKLineChart(chartContainer.value)
  
  // 生成模拟数据
  const mockData = generateMockData(100)
  
  // 应用数据
  chart.applyNewData(mockData)
  
  // 添加自定义指标
  if (compiledResult.value?.klineIndicator) {
    chart.createIndicator(compiledResult.value.klineIndicator, true)
  }
}

// 生成模拟K线数据
function generateMockData(count) {
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

// 保存指标
function saveIndicator() {
  if (!compiledResult.value?.success) {
    ElMessage.warning('请先编译成功后再保存')
    return
  }
  
  // 重置表单
  saveForm.value = {
    name: '',
    description: '',
    category: ''
  }
  
  showSaveDialog.value = true
}

// 确认保存
function confirmSave() {
  if (!saveForm.value.name.trim()) {
    ElMessage.warning('请输入指标名称')
    return
  }
  
  const indicator = {
    id: Date.now().toString(),
    name: saveForm.value.name,
    description: saveForm.value.description,
    category: saveForm.value.category,
    code: editor.getValue(),
    compiledResult: compiledResult.value,
    createTime: new Date().toISOString(),
    updateTime: new Date().toISOString()
  }
  
  // 保存到本地存储
  const saved = JSON.parse(localStorage.getItem('savedIndicators') || '[]')
  saved.push(indicator)
  localStorage.setItem('savedIndicators', JSON.stringify(saved))
  
  // 更新列表
  loadSavedIndicators()
  
  showSaveDialog.value = false
  ElMessage.success('指标保存成功！')
}

// 加载指标
function loadIndicator() {
  loadSavedIndicators()
  showLoadDialog.value = true
}

// 加载已保存的指标列表
function loadSavedIndicators() {
  const saved = JSON.parse(localStorage.getItem('savedIndicators') || '[]')
  savedIndicators.value = saved.map(item => ({
    ...item,
    updateTime: new Date(item.updateTime).toLocaleString()
  }))
}

// 选择指标
function selectIndicator(row) {
  selectedIndicatorId.value = row.id
}

// 确认加载
function confirmLoad() {
  const indicator = savedIndicators.value.find(item => item.id === selectedIndicatorId.value)
  if (!indicator) return
  
  // 加载代码到编辑器
  if (editor) {
    editor.setValue(indicator.code)
  }
  
  // 加载编译结果
  compiledResult.value = indicator.compiledResult
  
  showLoadDialog.value = false
  ElMessage.success('指标加载成功！')
}

// 删除指标
function deleteIndicator(id) {
  ElMessageBox.confirm('确定要删除这个指标吗？', '确认删除', {
    type: 'warning'
  }).then(() => {
    const saved = JSON.parse(localStorage.getItem('savedIndicators') || '[]')
    const filtered = saved.filter(item => item.id !== id)
    localStorage.setItem('savedIndicators', JSON.stringify(filtered))
    
    loadSavedIndicators()
    ElMessage.success('删除成功！')
  }).catch(() => {})
}

// 新建指标
function newIndicator() {
  ElMessageBox.confirm('确定要新建指标吗？当前未保存的内容将丢失。', '确认新建', {
    type: 'warning'
  }).then(() => {
    if (editor) {
      editor.setValue(templateCodes.custom)
    }
    compiledResult.value = null
    showPreview.value = false
    ElMessage.success('已创建新指标')
  }).catch(() => {})
}

// 加载模板
function loadTemplate() {
  if (!selectedTemplate.value) return
  
  const code = templateCodes[selectedTemplate.value]
  if (code && editor) {
    editor.setValue(code)
    compiledResult.value = null
  }
}

// 格式化代码
function formatCode() {
  if (editor) {
    editor.getAction('editor.action.formatDocument').run()
  }
}

// 切换全屏
function toggleFullscreen() {
  // 实现全屏逻辑
  ElMessage.info('全屏功能开发中...')
}

// 发送AI消息
function sendMessage() {
  if (!chatInput.value.trim()) return
  
  // 添加用户消息
  chatMessages.value.push({
    type: 'user',
    content: chatInput.value,
    timestamp: Date.now()
  })
  
  const userMessage = chatInput.value
  chatInput.value = ''
  aiProcessing.value = true
  
  // 模拟AI响应
  setTimeout(() => {
    const response = generateAIResponse(userMessage)
    chatMessages.value.push({
      type: 'assistant',
      content: response.message,
      timestamp: Date.now()
    })
    
    // 如果有生成的代码，应用到编辑器
    if (response.code && editor) {
      editor.setValue(response.code)
    }
    
    aiProcessing.value = false
    
    // 滚动到底部
    nextTick(() => {
      if (chatMessagesContainer.value) {
        chatMessagesContainer.value.scrollTop = chatMessagesContainer.value.scrollHeight
      }
    })
  }, 1000)
}

// 生成AI响应（模拟）
function generateAIResponse(message) {
  const lowerMessage = message.toLowerCase()
  
  if (lowerMessage.includes('双均线') || lowerMessage.includes('ma')) {
    return {
      message: '我为你生成了一个双均线指标，包含5日和20日移动平均线。当短期均线上穿长期均线时可能是买入信号。',
      code: templateCodes.dual_ma
    }
  }
  
  if (lowerMessage.includes('macd')) {
    return {
      message: '我为你生成了MACD指标，包含DIF线、DEA线和MACD柱。这是一个常用的趋势跟踪指标。',
      code: templateCodes.macd
    }
  }
  
  if (lowerMessage.includes('rsi')) {
    return {
      message: '我为你生成了RSI指标，包含6日、12日和24日RSI。RSI值在70以上可能超买，30以下可能超卖。',
      code: templateCodes.rsi
    }
  }
  
  if (lowerMessage.includes('kdj')) {
    return {
      message: '我为你生成了KDJ指标，这是一个随机震荡指标，K线和D线的交叉可以作为买卖信号。',
      code: templateCodes.kdj
    }
  }
  
  if (lowerMessage.includes('布林带') || lowerMessage.includes('boll')) {
    return {
      message: '我为你生成了布林带指标，包含上轨、中轨和下轨。价格触及上下轨时可能出现反转。',
      code: templateCodes.boll
    }
  }
  
  return {
    message: '我理解你想要创建一个自定义指标。请提供更具体的需求，比如：\n1. 使用哪些技术指标函数\n2. 计算周期参数\n3. 输出几条线\n4. 指标的具体逻辑\n\n我可以帮你生成相应的麦语言代码。',
    code: null
  }
}

// 关闭AI对话框
function handleAIDialogClose() {
  showAIDialog.value = false
}

// 格式化时间
function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString()
}

// 文件树相关方法
function refreshFileTree() {
  ElMessage.info('文件树刷新完成')
}

function handleFileSelect(data) {
  selectedFileNode.value = data
  if (data.type === 'file') {
    openFileInEditor(data)
  }
}

function openFileInEditor(fileData) {
  // 检查是否已经打开
  const existingTab = editorTabs.value.find(tab => tab.id === fileData.id)
  if (existingTab) {
    activeEditorTab.value = existingTab.id
    return
  }
  
  // 创建新标签页
  const newTab = {
    id: fileData.id,
    name: fileData.label,
    code: templateCodes[fileData.id] || templateCodes.custom,
    saved: true
  }
  
  editorTabs.value.push(newTab)
  activeEditorTab.value = newTab.id
  
  // 在下一个tick中初始化编辑器
  nextTick(() => {
    initTabEditor(newTab.id)
  })
}

function closeTab(tabId) {
  const tabIndex = editorTabs.value.findIndex(tab => tab.id === tabId)
  if (tabIndex === -1) return
  
  const tab = editorTabs.value[tabIndex]
  
  // 如果有未保存的更改，提示用户
  if (!tab.saved) {
    ElMessageBox.confirm('文件有未保存的更改，确定要关闭吗？', '确认关闭', {
      type: 'warning'
    }).then(() => {
      doCloseTab(tabId, tabIndex)
    }).catch(() => {})
  } else {
    doCloseTab(tabId, tabIndex)
  }
}

function doCloseTab(tabId, tabIndex) {
  // 销毁编辑器实例
  const editorInstance = editorRefs.value.get(tabId)
  if (editorInstance) {
    editorInstance.dispose()
    editorRefs.value.delete(tabId)
  }
  
  // 移除标签页
  editorTabs.value.splice(tabIndex, 1)
  
  // 如果关闭的是当前活动标签页，切换到其他标签页
  if (activeEditorTab.value === tabId) {
    if (editorTabs.value.length > 0) {
      const newIndex = Math.min(tabIndex, editorTabs.value.length - 1)
      activeEditorTab.value = editorTabs.value[newIndex].id
    } else {
      activeEditorTab.value = ''
    }
  }
}



function initTabEditor(tabId) {
  const container = document.querySelector(`[data-tab-id="${tabId}"]`)
  if (!container) return
  
  const tab = editorTabs.value.find(t => t.id === tabId)
  if (!tab) return
  
  // 创建编辑器实例
  const editorInstance = monaco.editor.create(container, {
    value: tab.code,
    language: 'mailang',
    theme: 'mailang-theme',
    fontSize: 14,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    wordWrap: 'on',
    lineNumbers: 'on',
    glyphMargin: true,
    folding: true,
    lineDecorationsWidth: 10,
    lineNumbersMinChars: 3
  })
  
  // 监听内容变化
  editorInstance.onDidChangeModelContent(() => {
    tab.code = editorInstance.getValue()
    tab.saved = false
    compiledResult.value = null
  })
  
  // 存储编辑器实例
  editorRefs.value.set(tabId, editorInstance)
}

// 文件操作方法
function createNewFile() {
  ElMessageBox.prompt('请输入文件名', '新建指标文件', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /^[\w\u4e00-\u9fa5]+$/,
    inputErrorMessage: '文件名只能包含字母、数字、下划线和中文'
  }).then(({ value }) => {
    const newFile = {
      id: `custom_${Date.now()}`,
      label: `${value}.mai`,
      type: 'file'
    }
    
    // 添加到自定义指标文件夹
    const customFolder = findNodeById(fileTreeData.value, 'custom')
    if (customFolder) {
      customFolder.children.push(newFile)
      ElMessage.success('文件创建成功')
    }
  }).catch(() => {})
}

function copyFile() {
  // 基于当前激活的编辑器标签页来确定要复制的文件
  if (!activeEditorTab.value) {
    ElMessage.warning('请先打开一个文件')
    return
  }
  
  // 从当前激活的标签页获取文件信息
  const activeTab = editorTabs.value.find(tab => tab.id === activeEditorTab.value)
  if (!activeTab) {
    ElMessage.warning('未找到当前激活的文件')
    return
  }
  
  // 在文件树中找到对应的文件节点
  const originalFile = findNodeById(fileTreeData.value, activeTab.id)
  if (!originalFile || originalFile.type !== 'file') {
    ElMessage.warning('未找到对应的文件节点')
    return
  }
  const copyName = `${originalFile.label.replace('.mai', '')}_副本.mai`
  
  const newFile = {
    id: `copy_${Date.now()}`,
    label: copyName,
    type: 'file'
  }
  
  // 添加到同一个文件夹，紧邻原文件
  console.log('原文件ID:', originalFile.id)
  console.log('文件树结构:', fileTreeData.value[0].children)
  const parentFolder = findParentNode(fileTreeData.value[0].children, originalFile.id)
  console.log('找到的父文件夹:', parentFolder)
  if (parentFolder && parentFolder.children) {
    // 找到原文件在children数组中的索引
    const originalIndex = parentFolder.children.findIndex(child => child.id === originalFile.id)
    console.log('原文件索引:', originalIndex)
    if (originalIndex !== -1) {
      // 在原文件的下一个位置插入复制的文件
      parentFolder.children.splice(originalIndex + 1, 0, newFile)
    } else {
      // 如果找不到原文件索引，则添加到末尾
      parentFolder.children.push(newFile)
    }
    ElMessage.success('文件复制成功')
  } else {
    console.log('未找到父文件夹，添加到自定义指标')
    // 如果找不到父文件夹，添加到自定义指标分组
    const customFolder = fileTreeData.value[0].children.find(folder => folder.id === 'custom')
    if (customFolder) {
      customFolder.children.push(newFile)
      ElMessage.success('文件复制成功')
    }
  }
}

function deleteFile() {
  if (!selectedFileNode.value) {
    ElMessage.warning('请先选择一个文件或文件夹')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除 "${selectedFileNode.value.label}" 吗？此操作不可恢复。`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    removeNodeFromTree(fileTreeData.value, selectedFileNode.value.id)
    selectedFileNode.value = null
    ElMessage.success('删除成功')
  }).catch(() => {})
}

function renameFile() {
  if (!selectedFileNode.value) {
    ElMessage.warning('请先选择一个文件或文件夹')
    return
  }
  
  const currentName = selectedFileNode.value.label.replace('.mai', '')
  
  ElMessageBox.prompt('请输入新名称', '重命名', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: currentName,
    inputPattern: /^[\w\u4e00-\u9fa5]+$/,
    inputErrorMessage: '名称只能包含字母、数字、下划线和中文'
  }).then(({ value }) => {
    const newLabel = selectedFileNode.value.type === 'file' ? `${value}.mai` : value
    selectedFileNode.value.label = newLabel
    ElMessage.success('重命名成功')
  }).catch(() => {})
}

// 辅助方法
function findNodeById(nodes, id) {
  for (const node of nodes) {
    if (node.id === id) {
      return node
    }
    if (node.children) {
      const found = findNodeById(node.children, id)
      if (found) return found
    }
  }
  return null
}

function findParentNode(nodes, childId, parent = null) {
  for (const node of nodes) {
    if (node.children) {
      if (node.children.some(child => child.id === childId)) {
        return node
      }
      const found = findParentNode(node.children, childId, node)
      if (found) return found
    }
  }
  return parent
}

function removeNodeFromTree(nodes, id) {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].id === id) {
      nodes.splice(i, 1)
      return true
    }
    if (nodes[i].children) {
      if (removeNodeFromTree(nodes[i].children, id)) {
        return true
      }
    }
  }
  return false
}

// 拖拽相关方法
function allowDrag(draggingNode) {
  // 允许拖拽文件，但不允许拖拽根文件夹
  return draggingNode.data.id !== 'indicators'
}

function allowDrop(draggingNode, dropNode, type) {
  // 不允许拖拽到根文件夹之外
  if (dropNode.data.id === 'indicators' && type !== 'inner') {
    return false
  }
  
  // 文件只能拖拽到文件夹内部或文件之间
  if (draggingNode.data.type === 'file') {
    if (type === 'inner') {
      // 只能拖拽到文件夹内部
      return dropNode.data.type === 'folder'
    } else {
      // 可以拖拽到其他文件的前后
      return dropNode.data.type === 'file'
    }
  }
  
  // 文件夹可以拖拽到其他文件夹内部或文件夹之间
  if (draggingNode.data.type === 'folder') {
    if (type === 'inner') {
      return dropNode.data.type === 'folder' && dropNode.data.id !== draggingNode.data.id
    } else {
      return dropNode.data.type === 'folder'
    }
  }
  
  return true
}

function handleNodeDrop(draggingNode, dropNode, dropType, ev) {
  ElMessage.success(`已将 "${draggingNode.data.label}" 移动到新位置`)
  
  // 如果拖拽的是已打开的文件，更新标签页信息
  if (draggingNode.data.type === 'file') {
    const tab = editorTabs.value.find(t => t.id === draggingNode.data.id)
    if (tab) {
      tab.name = draggingNode.data.label
    }
  }
}

// AI面板相关方法
function toggleAIPanel() {
  showAIPanel.value = !showAIPanel.value
}
</script>

<style scoped>
.indicator-ide {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-primary);
}

.ide-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: var(--tv-bg-secondary);
  border-bottom: 1px solid var(--tv-border-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 48px;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* T型布局主体 */
.ide-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧文件树面板 */
.file-tree-panel {
  width: 250px;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-secondary);
  border-right: 1px solid var(--tv-border-primary);
  flex-shrink: 0;
}

.file-tree-content {
  flex: 1;
  overflow: auto;
  padding: 8px;
}

.file-tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
}

.node-label {
  font-size: 13px;
}

/* 右侧IDE面板 */
.ide-right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-secondary);
  overflow: hidden;
}

/* 编辑器区域 */
.editor-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-tabs .el-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-tabs .el-tabs__content {
  flex: 1;
  overflow: hidden;
}

.editor-tabs .el-tab-pane {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.welcome-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--tv-bg-primary);
}

.welcome-content {
  text-align: center;
  color: var(--tv-text-secondary);
}

.welcome-content h3 {
  margin: 0 0 16px 0;
  color: var(--tv-text-primary);
}

.welcome-content p {
  margin: 0 0 24px 0;
  font-size: 14px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--tv-bg-overlay);
  border-bottom: 1px solid var(--tv-border-primary);
  font-weight: 500;
  font-size: 13px;
  height: 36px;
  flex-shrink: 0;
  color: var(--tv-text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.editor-container {
  flex: 1;
  min-height: 0;
  border: none;
  border-radius: 0;
}

.tab-editor-container {
  flex: 1;
  overflow: hidden;
}

.compile-result {
  height: 200px;
  border-top: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-secondary);
  flex-shrink: 0;
}

.result-header {
  padding: 8px 16px;
  background: var(--tv-bg-overlay);
  border-bottom: 1px solid var(--tv-border-primary);
}

.result-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.result-status.success {
  color: var(--tv-success);
}

.result-status.error {
  color: var(--tv-danger);
}

.result-content {
  height: calc(100% - 40px);
  overflow: auto;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  background: var(--tv-bg-primary);
  color: var(--tv-text-primary);
}

/* Element Plus 组件样式覆盖 */
:deep(.el-tree) {
  background: transparent !important;
  color: var(--tv-text-primary) !important;
}

:deep(.el-tree-node__content) {
  background: transparent !important;
  color: var(--tv-text-primary) !important;
}

:deep(.el-tree-node__content:hover) {
  background: var(--tv-bg-hover) !important;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: var(--tv-accent-primary) !important;
  color: var(--tv-text-on-accent) !important;
}

:deep(.el-button) {
  background: var(--tv-bg-overlay) !important;
  border-color: var(--tv-border-primary) !important;
  color: var(--tv-text-primary) !important;
}

:deep(.el-button:hover) {
  background: var(--tv-bg-hover) !important;
  border-color: var(--tv-border-secondary) !important;
}

:deep(.el-button--primary) {
  background: var(--tv-accent-primary) !important;
  border-color: var(--tv-accent-primary) !important;
  color: var(--tv-text-on-accent) !important;
}

:deep(.el-select .el-input .el-input__wrapper) {
  background: var(--tv-bg-overlay) !important;
  border-color: var(--tv-border-primary) !important;
}

:deep(.el-select .el-input .el-input__inner) {
  color: var(--tv-text-primary) !important;
}

:deep(.el-select .el-input .el-input__wrapper) {
  background: var(--tv-bg-overlay) !important;
  border-color: var(--tv-border-primary) !important;
}

:deep(.el-select .el-select__wrapper) {
  background: var(--tv-bg-overlay) !important;
  border-color: var(--tv-border-primary) !important;
}

:deep(.el-select .el-select__selection) {
  background: transparent !important;
}

:deep(.el-select .el-select__placeholder) {
  color: var(--tv-text-secondary) !important;
}

:deep(.el-tabs__header) {
  background: var(--tv-bg-secondary) !important;
  border-bottom: 1px solid var(--tv-border-primary) !important;
}

:deep(.el-tabs__item) {
  background: var(--tv-bg-overlay) !important;
  border-color: var(--tv-border-primary) !important;
  color: var(--tv-text-primary) !important;
}

:deep(.el-tabs__item.is-active) {
  background: var(--tv-bg-primary) !important;
  color: var(--tv-text-primary) !important;
}

:deep(.el-tabs__content) {
  background: var(--tv-bg-primary) !important;
}

/* 下拉框选项样式 */
:deep(.el-select-dropdown) {
  background: var(--tv-bg-overlay) !important;
  border-color: var(--tv-border-primary) !important;
}

:deep(.el-select-dropdown .el-select-dropdown__item) {
    background: transparent !important;
    color: var(--tv-text-primary) !important;
    border: 1px solid transparent !important;
    transition: all 0.2s ease !important;
    margin: 1px !important;
    border-radius: 2px !important;
    box-sizing: border-box !important;
  }
  
  :deep(.el-select-dropdown .el-select-dropdown__item:hover),
  :deep(.el-select-dropdown__item.is-hovering),
  :deep(.el-select-dropdown__item:focus) {
    background: var(--tv-bg-hover) !important;
    border: 1px solid #2196F3 !important;
    color: var(--tv-text-primary) !important;
    box-shadow: 0 0 0 1px #2196F3 !important;
  }

:deep(.el-select-dropdown__item.selected) {
  background: var(--tv-accent-primary) !important;
  color: var(--tv-text-on-accent) !important;
}

/* 欢迎面板样式 */
.welcome-panel {
  background: var(--tv-bg-primary) !important;
  color: var(--tv-text-primary) !important;
}

.welcome-content {
  background: transparent !important;
}

.welcome-content h3 {
  color: var(--tv-text-primary) !important;
}

.welcome-content p {
  color: var(--tv-text-secondary) !important;
}

/* AI面板样式 */
.ai-input-panel {
  height: 300px;
  border-top: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-secondary);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.ai-input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--tv-bg-overlay);
  border-bottom: 1px solid var(--tv-border-primary);
  font-weight: 500;
  font-size: 13px;
  height: 36px;
  color: var(--tv-text-primary);
}

.ai-chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: var(--tv-bg-primary);
}

.chat-input {
  padding: 12px;
  border-top: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-secondary);
}

.input-actions {
  margin-top: 8px;
  text-align: right;
}

.message {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message.user .message-content {
  background: var(--tv-primary);
  color: var(--tv-text-inverse);
}

.message.assistant .message-content {
  background: var(--tv-bg-overlay);
  border: 1px solid var(--tv-border-primary);
  color: var(--tv-text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--tv-text-secondary);
  margin-top: 4px;
  text-align: center;
}

.code-output,
.error-message {
  padding: 16px;
  margin: 0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.error-message {
  color: var(--tv-danger);
  background: var(--tv-color-down-bg);
}

.preview-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chart-preview {
  height: 300px;
  border-bottom: 1px solid var(--tv-border-primary);
}

.indicator-info {
  flex: 1;
  padding: 16px;
  overflow: auto;
}

.indicator-info h4 {
  margin: 0 0 12px 0;
  color: var(--tv-text-primary);
}

.color-indicator {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 2px;
  margin-right: 8px;
  vertical-align: middle;
}

.ai-chat {
  height: 500px;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: var(--tv-bg-primary);
}

.message {
  margin-bottom: 16px;
}

.message.user {
  text-align: right;
}

.message.user .message-content {
  background: var(--tv-primary);
  color: var(--tv-text-inverse);
  display: inline-block;
  padding: 8px 12px;
  border-radius: 12px;
  max-width: 80%;
  word-wrap: break-word;
}

.message.assistant .message-content {
  background: var(--tv-bg-overlay);
  border: 1px solid var(--tv-border-primary);
  display: inline-block;
  padding: 8px 12px;
  border-radius: 12px;
  max-width: 80%;
  word-wrap: break-word;
}

.message-time {
  font-size: 12px;
  color: var(--tv-text-secondary);
  margin-top: 4px;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid var(--tv-border-primary);
}

.input-actions {
  margin-top: 8px;
  text-align: right;
}
</style>