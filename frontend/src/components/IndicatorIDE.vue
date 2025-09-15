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
        
        <el-button-group style="margin-left: 8px;">
          <el-tooltip content="撤销">
            <el-button :icon="RefreshLeft" @click="undoEdit" size="small" :disabled="!activeEditorTab">撤销</el-button>
          </el-tooltip>
          <el-tooltip content="清空">
            <el-button :icon="DeleteFilled" @click="clearEditor" size="small" :disabled="!activeEditorTab">清空</el-button>
          </el-tooltip>
          <el-tooltip content="保存">
            <el-button :icon="FolderAdd" @click="saveIndicator" size="small" :disabled="!activeEditorTab">保存</el-button>
          </el-tooltip>
          <el-tooltip content="编译">
            <el-button :icon="CompileIcon" @click="compileCode" size="small" :disabled="!activeEditorTab">编译</el-button>
          </el-tooltip>
          <el-tooltip content="加载">
            <el-button :icon="LoadIcon" @click="loadIndicator" size="small">加载</el-button>
          </el-tooltip>
          <el-tooltip content="移除">
            <el-button :icon="CloseBold" @click="removeIndicator" size="small" :disabled="!activeEditorTab">移除</el-button>
          </el-tooltip>
          <el-tooltip content="收藏">
            <el-button :icon="Star" @click="favoriteIndicator" size="small" :disabled="!activeEditorTab">收藏</el-button>
          </el-tooltip>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
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
      
      <!-- 右侧新容器 -->
      <div class="right-panel">
        <div class="panel-header">
          <h3>功能面板</h3>
        </div>
        <div class="panel-content">
          <p>这里可以添加其他功能模块</p>
        </div>
      </div>
    </div>
    

    
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

// 定义emit事件
const emit = defineEmits(['show-indicator-dialog'])
import {
  CaretRight,
  VideoPlay,
  Download,
  FolderOpened,
  DocumentAdd,
  MagicStick,
  FullScreen,
  Close,
  Check,
  Refresh,
  Folder,
  Document,
  CopyDocument,
  Delete,
  Edit,
  RefreshLeft,
  DeleteFilled,
  FolderAdd,
  CaretRight as CompileIcon,
  FolderOpened as LoadIcon,
  CloseBold,
  Star
} from '@element-plus/icons-vue'
import * as monaco from 'monaco-editor'
import { maiLangCompiler } from '@/utils/maiLangCompiler'
import { indicatorsManager } from '@/utils/indicatorsManager'
import { init as initKLineChart, dispose as disposeKLineChart } from 'klinecharts'

// 响应式数据
const chartContainer = ref(null)

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
const showSaveDialog = ref(false)
const showLoadDialog = ref(false)

const activeResultTab = ref('js')
const selectedIndicatorId = ref(null)
const selectedFileNode = ref(null)

// 编辑器和图表实例
let chart = null
const closingTabs = new Set() // 正在关闭的标签页集合

// 编译结果
const compiledResult = ref(null)



// 保存表单
const saveForm = ref({
  name: '',
  description: '',
  category: ''
})

// 已保存的指标
const savedIndicators = ref([])





// 组件挂载
onMounted(async () => {
  await nextTick()
  await initMonacoLanguage()
  loadSavedIndicators()
})

// 组件卸载
onUnmounted(() => {
  // 清理所有编辑器实例
  editorRefs.value.forEach(editor => {
    editor.dispose()
  })
  editorRefs.value.clear()
  
  if (chart) {
    disposeKLineChart(chart)
  }
})

// 初始化Monaco语言配置
async function initMonacoLanguage() {
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
  
  // Monaco语言配置完成
}

// 获取当前活跃的编辑器实例
function getCurrentEditor() {
  if (!activeEditorTab.value) return null
  const editorData = editorRefs.value.get(activeEditorTab.value)
  return editorData?.editor || null
}

// 编译代码
async function compileCode() {
  const editor = getCurrentEditor()
  if (!editor) return
  
  compiling.value = true
  const code = editor.getValue()
  
  try {
    const result = maiLangCompiler.compile(code)
    compiledResult.value = result
    
    if (result.success) {
      ElMessage.success('编译成功！')
      
      // 自动保存到indicators文件夹
      const currentTab = editorTabs.value.find(tab => tab.id === activeEditorTab.value)
      if (currentTab && currentTab.name !== '新建指标') {
        const indicatorName = currentTab.name.replace('.mai', '')
        const category = detectIndicatorCategory(result.indicatorsFormat)
        
        try {
          const saveResult = await indicatorsManager.compileAndSave(
            code,
            indicatorName,
            category
          )
          
          if (saveResult.success) {
            ElMessage.success(`指标已自动保存到indicators/${category}文件夹`)
          } else {
            console.warn('自动保存失败:', saveResult.message)
          }
        } catch (saveError) {
          console.warn('自动保存过程中出错:', saveError.message)
        }
      }
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

// 检测指标类型（主图/副图）
function detectIndicatorCategory(indicatorsFormat) {
  if (!indicatorsFormat || !indicatorsFormat.figures) {
    return 'sub' // 默认为副图
  }
  
  // 检查是否有baseValue为null的图形（主图指标特征）
  const hasMainChartFigure = indicatorsFormat.figures.some(figure => 
    figure.baseValue === null
  )
  
  return hasMainChartFigure ? 'main' : 'sub'
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
  const editor = getCurrentEditor()
  if (!editor) return
  
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
  const editor = getCurrentEditor()
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


// 撤销编辑
function undoEdit() {
  const editor = getCurrentEditor()
  if (editor) {
    editor.trigger('keyboard', 'undo', null)
    ElMessage.success('已撤销')
  }
}

// 清空编辑器
async function clearEditor() {
  const editor = getCurrentEditor()
  if (!editor) {
    ElMessage.warning('请先选择一个编辑器标签页')
    return
  }
  
  // 先获取当前标签页
  const currentTab = editorTabs.value.find(tab => tab.id === activeEditorTab.value)
  if (!currentTab) {
    ElMessage.error('未找到当前标签页')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '确定要清空当前编辑器内容吗？',
      '确认清空',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    // 用户确认后执行清空操作
    try {
      // 直接设置编辑器内容为空
      const model = editor.getModel()
      if (model) {
        model.setValue('')
      } else {
        editor.setValue('')
      }
      
      // 更新标签页状态
      currentTab.code = ''
      currentTab.saved = false
      compiledResult.value = null
      
      ElMessage.success('编辑器已清空')
    } catch (error) {
      console.error('清空编辑器时出错:', error)
      ElMessage.error('清空编辑器失败: ' + error.message)
    }
  } catch (error) {
    // 用户取消操作或其他错误
    if (error !== 'cancel') {
      console.error('确认对话框出错:', error)
      ElMessage.error('操作失败，请重试')
    }
  }
}

// 移除指标
function removeIndicator() {
  const editor = getCurrentEditor()
  if (!editor) return
  
  const currentTab = editorTabs.value.find(tab => tab.id === activeEditorTab.value)
  if (!currentTab) return
  
  ElMessageBox.confirm('确定要移除当前指标吗？', '确认移除', {
    type: 'warning'
  }).then(() => {
    // 关闭当前标签页
    closeTab(currentTab.id)
    ElMessage.success('指标已移除')
  }).catch(() => {})
}

// 收藏指标
function favoriteIndicator() {
  const editor = getCurrentEditor()
  if (!editor) return
  
  const currentTab = editorTabs.value.find(tab => tab.id === activeEditorTab.value)
  if (!currentTab) return
  
  // 获取收藏列表
  const favorites = JSON.parse(localStorage.getItem('favoriteIndicators') || '[]')
  
  // 检查是否已收藏
  const isAlreadyFavorite = favorites.some(fav => fav.name === currentTab.name)
  
  if (isAlreadyFavorite) {
    ElMessage.warning('该指标已在收藏夹中')
    return
  }
  
  // 添加到收藏
  const favorite = {
    id: Date.now().toString(),
    name: currentTab.name,
    code: editor.getValue(),
    createTime: new Date().toISOString()
  }
  
  favorites.push(favorite)
  localStorage.setItem('favoriteIndicators', JSON.stringify(favorites))
  
  // 发射事件通知父组件打开指标弹窗
  emit('show-indicator-dialog')
  
  ElMessage.success('已添加到收藏夹，正在打开指标弹窗')
}

// 格式化代码
function formatCode() {
  const editor = getCurrentEditor()
  if (editor) {
    editor.getAction('editor.action.formatDocument').run()
  }
}

// 切换全屏
function toggleFullscreen() {
  // 实现全屏逻辑
  ElMessage.info('全屏功能开发中...')
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
    code: '// 请在此处编写您的指标代码\n',
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
  // 防止重复关闭
  if (closingTabs.has(tabId)) return
  
  const tabIndex = editorTabs.value.findIndex(tab => tab.id === tabId)
  if (tabIndex === -1) return
  
  const tab = editorTabs.value[tabIndex]
  if (!tab) return
  
  closingTabs.add(tabId)
  
  // 如果有未保存的更改，提示用户
  if (!tab.saved) {
    ElMessageBox.confirm('文件有未保存的更改，确定要关闭吗？', '确认关闭', {
      type: 'warning',
      beforeClose: (action, instance, done) => {
        if (action === 'confirm') {
          doCloseTab(tabId, tabIndex)
        }
        done()
      }
    }).catch(() => {
       // 用户取消关闭，清理关闭状态
       closingTabs.delete(tabId)
     })
  } else {
    doCloseTab(tabId, tabIndex)
  }
}

function doCloseTab(tabId, tabIndex) {
  // 先切换活动标签页，避免在销毁过程中访问已销毁的编辑器
  if (activeEditorTab.value === tabId) {
    if (editorTabs.value.length > 1) {
      const newIndex = tabIndex === 0 ? 1 : tabIndex - 1
      activeEditorTab.value = editorTabs.value[newIndex].id
    } else {
      activeEditorTab.value = ''
    }
  }
  
  // 获取编辑器实例并销毁
  const editorData = editorRefs.value.get(tabId)
  if (editorData) {
    try {
      // 先销毁所有事件监听器
      if (editorData.disposables) {
        editorData.disposables.forEach(disposable => {
          try {
            disposable.dispose()
          } catch (e) {
            console.warn('销毁事件监听器时出错:', e)
          }
        })
      }
      
      // 销毁编辑器模型和实例
      if (editorData.editor) {
        editorData.editor.getModel()?.dispose()
        editorData.editor.dispose()
      }
    } catch (error) {
      console.warn('编辑器销毁时出错:', error)
    }
    editorRefs.value.delete(tabId)
  }
  
  // 使用nextTick确保编辑器完全销毁后再移除DOM
  nextTick(() => {
    // 移除标签页
    editorTabs.value.splice(tabIndex, 1)
    
    // 清理关闭状态
    closingTabs.delete(tabId)
  })
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
  const contentChangeDisposable = editorInstance.onDidChangeModelContent(() => {
    tab.code = editorInstance.getValue()
    tab.saved = false
    compiledResult.value = null
  })
  
  // 存储编辑器实例和事件监听器
  editorRefs.value.set(tabId, {
    editor: editorInstance,
    disposables: [contentChangeDisposable]
  })
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
  height: calc(100vh - 48px); /* 减去工具栏高度 */
}

/* 文件树面板 */
.file-tree-panel {
  width: 250px; /* 固定宽度 */
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-secondary);
  border-right: 1px solid var(--tv-border-color); /* 恢复右边框 */
  flex-shrink: 0;
  height: 100%; /* 确保高度填满父容器 */
}

/* 右侧新容器 */
.right-panel {
  flex: 1; /* 占据剩余空间 */
  display: flex;
  flex-direction: column;
  background: #131722; /* 直接使用颜色值 */
  height: 100%; /* 确保高度填满父容器 */
  min-height: 100%; /* 添加最小高度 */
}

.panel-header {
  padding: 12px 16px;
  background: #131722; /* 直接使用颜色值 */
  border-bottom: 1px solid var(--tv-border-primary);
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--tv-text-primary);
}

.panel-content {
  flex: 1;
  padding: 16px;
  overflow: auto;
  color: var(--tv-text-secondary);
  position: relative;
  z-index: 9999;
}

.file-tree-content {
  flex: 1;
  overflow: auto;
  padding: 8px;
  background-color: white;
}

.file-tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
}

.node-label {
  font-size: 13px;
}

/* 编辑器相关样式已完全移除 */

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
  overflow: hidden;
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


</style>
