<template>
  <div class="indicator-manager">
    <!-- 管理器头部 -->
    <div class="manager-header">
      <div class="header-left">
        <el-icon class="manager-icon"><FolderOpened /></el-icon>
        <span class="manager-title">指标管理器</span>
        <el-tag size="small" type="info">{{ totalIndicators }}个指标</el-tag>
      </div>
      
      <div class="header-right">
        <el-button-group size="small">
          <el-button :icon="Plus" type="primary" @click="createNewIndicator">新建</el-button>
          <el-button :icon="Upload" @click="importIndicators">导入</el-button>
          <el-button :icon="Download" @click="exportIndicators">导出</el-button>
          <el-button :icon="Refresh" @click="refreshIndicators">刷新</el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="search-filter">
      <div class="search-bar">
        <el-input 
          v-model="searchQuery" 
          placeholder="搜索指标名称、描述或标签..."
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
        />
      </div>
      
      <div class="filter-bar">
        <el-select 
          v-model="selectedCategory" 
          placeholder="分类"
          clearable
          @change="handleFilter"
          style="width: 120px"
        >
          <el-option 
            v-for="category in categories" 
            :key="category.value" 
            :label="category.label" 
            :value="category.value"
          />
        </el-select>
        
        <el-select 
          v-model="selectedStatus" 
          placeholder="状态"
          clearable
          @change="handleFilter"
          style="width: 100px"
        >
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
          <el-option label="已归档" value="archived" />
        </el-select>
        
        <el-select 
          v-model="sortBy" 
          placeholder="排序"
          @change="handleSort"
          style="width: 120px"
        >
          <el-option label="创建时间" value="created_at" />
          <el-option label="修改时间" value="updated_at" />
          <el-option label="名称" value="name" />
          <el-option label="使用次数" value="usage_count" />
        </el-select>
        
        <el-button 
          :icon="sortOrder === 'asc' ? 'SortUp' : 'SortDown'" 
          @click="toggleSortOrder"
          size="small"
        />
      </div>
    </div>
    
    <!-- 指标列表 -->
    <div class="indicator-list">
      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="list-view">
        <el-table 
          :data="filteredIndicators" 
          @selection-change="handleSelectionChange"
          @row-click="handleRowClick"
          stripe
          style="width: 100%"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column prop="name" label="名称" min-width="150">
            <template #default="{ row }">
              <div class="indicator-name">
                <el-icon class="indicator-icon">{{ getIndicatorIcon(row.category) }}</el-icon>
                <span>{{ row.name }}</span>
                <el-tag v-if="row.is_favorite" size="small" type="warning">收藏</el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          
          <el-table-column prop="category" label="分类" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="getCategoryType(row.category)">{{ getCategoryLabel(row.category) }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="version" label="版本" width="80" />
          
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag size="small" :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="usage_count" label="使用次数" width="100" />
          
          <el-table-column prop="updated_at" label="修改时间" width="150">
            <template #default="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button-group size="small">
                <el-button :icon="Edit" @click.stop="editIndicator(row)">编辑</el-button>
                <el-button :icon="CopyDocument" @click.stop="duplicateIndicator(row)">复制</el-button>
                <el-button :icon="Star" @click.stop="toggleFavorite(row)" :type="row.is_favorite ? 'warning' : 'default'">{{ row.is_favorite ? '取消收藏' : '收藏' }}</el-button>
                <el-dropdown @command="handleCommand" trigger="click">
                  <el-button :icon="More" size="small" />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'export', row }">导出</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'share', row }">分享</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'history', row }">版本历史</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'archive', row }" v-if="row.status !== 'archived'">归档</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'restore', row }" v-if="row.status === 'archived'">恢复</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'delete', row }" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <!-- 卡片视图 -->
      <div v-else class="card-view">
        <div class="card-grid">
          <div 
            v-for="indicator in filteredIndicators" 
            :key="indicator.id" 
            class="indicator-card"
            @click="handleCardClick(indicator)"
          >
            <div class="card-header">
              <div class="card-title">
                <el-icon class="card-icon">{{ getIndicatorIcon(indicator.category) }}</el-icon>
                <span>{{ indicator.name }}</span>
              </div>
              
              <div class="card-actions">
                <el-button 
                  :icon="Star" 
                  size="small" 
                  :type="indicator.is_favorite ? 'warning' : 'default'"
                  @click.stop="toggleFavorite(indicator)"
                  circle
                />
                <el-dropdown @command="handleCommand" trigger="click" @click.stop>
                  <el-button :icon="More" size="small" circle />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'edit', row: indicator }">编辑</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'duplicate', row: indicator }">复制</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'export', row: indicator }">导出</el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'delete', row: indicator }" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <div class="card-content">
              <p class="card-description">{{ indicator.description || '暂无描述' }}</p>
              
              <div class="card-tags">
                <el-tag size="small" :type="getCategoryType(indicator.category)">{{ getCategoryLabel(indicator.category) }}</el-tag>
                <el-tag size="small" :type="getStatusType(indicator.status)">{{ getStatusLabel(indicator.status) }}</el-tag>
              </div>
            </div>
            
            <div class="card-footer">
              <div class="card-meta">
                <span class="version">v{{ indicator.version }}</span>
                <span class="usage">使用{{ indicator.usage_count }}次</span>
              </div>
              
              <div class="card-time">
                {{ formatDate(indicator.updated_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="filteredIndicators.length === 0" class="empty-state">
        <el-empty description="暂无指标">
          <el-button type="primary" :icon="Plus" @click="createNewIndicator">创建第一个指标</el-button>
        </el-empty>
      </div>
    </div>
    
    <!-- 底部工具栏 -->
    <div class="bottom-toolbar" v-if="selectedIndicators.length > 0">
      <div class="toolbar-left">
        <span>已选择 {{ selectedIndicators.length }} 个指标</span>
      </div>
      
      <div class="toolbar-right">
        <el-button-group size="small">
          <el-button :icon="Download" @click="batchExport">批量导出</el-button>
          <el-button :icon="Star" @click="batchFavorite">批量收藏</el-button>
          <el-button :icon="Box" @click="batchArchive">批量归档</el-button>
          <el-button :icon="Delete" type="danger" @click="batchDelete">批量删除</el-button>
        </el-button-group>
      </div>
    </div>
    
    <!-- 视图切换 -->
    <div class="view-toggle">
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button label="list">列表</el-radio-button>
        <el-radio-button label="card">卡片</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 新建/编辑指标对话框 -->
    <el-dialog 
      v-model="showIndicatorDialog" 
      :title="editingIndicator ? '编辑指标' : '新建指标'"
      width="600px"
      @close="resetIndicatorForm"
    >
      <el-form 
        ref="indicatorFormRef" 
        :model="indicatorForm" 
        :rules="indicatorRules" 
        label-width="100px"
      >
        <el-form-item label="指标名称" prop="name">
          <el-input v-model="indicatorForm.name" placeholder="请输入指标名称" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="indicatorForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option 
              v-for="category in categories" 
              :key="category.value" 
              :label="category.label" 
              :value="category.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input 
            v-model="indicatorForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入指标描述"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-tag 
            v-for="tag in indicatorForm.tags" 
            :key="tag" 
            closable 
            @close="removeTag(tag)"
            style="margin-right: 8px"
          >
            {{ tag }}
          </el-tag>
          
          <el-input 
            v-if="inputVisible" 
            ref="inputRef" 
            v-model="inputValue" 
            size="small" 
            style="width: 100px" 
            @keyup.enter="handleInputConfirm" 
            @blur="handleInputConfirm"
          />
          
          <el-button v-else size="small" @click="showInput">+ 添加标签</el-button>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-radio-group v-model="indicatorForm.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="published">已发布</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="代码" prop="code">
          <div class="code-editor-container">
            <div ref="codeEditorRef" class="code-editor"></div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showIndicatorDialog = false">取消</el-button>
        <el-button type="primary" @click="saveIndicator" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 版本历史对话框 -->
    <el-dialog v-model="showHistoryDialog" title="版本历史" width="800px">
      <el-timeline>
        <el-timeline-item 
          v-for="version in versionHistory" 
          :key="version.id" 
          :timestamp="formatDate(version.created_at)"
        >
          <div class="version-item">
            <div class="version-header">
              <span class="version-number">v{{ version.version }}</span>
              <span class="version-author">{{ version.author }}</span>
              <el-button size="small" @click="restoreVersion(version)">恢复此版本</el-button>
            </div>
            <div class="version-changes">{{ version.changes }}</div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>
    
    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入指标" width="500px">
      <el-upload 
        ref="uploadRef" 
        :auto-upload="false" 
        :on-change="handleFileChange" 
        accept=".json,.mai"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 .json 和 .mai 格式文件</div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  FolderOpened,
  Plus,
  Upload,
  Download,
  Refresh,
  Search,
  Edit,
  CopyDocument,
  Star,
  More,
  Delete,
  Box,
  UploadFilled
} from '@element-plus/icons-vue'
import * as monaco from 'monaco-editor'

// Props & Emits
const emit = defineEmits(['edit-indicator', 'create-indicator'])

// 响应式数据
const indicators = ref([])
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedStatus = ref('')
const sortBy = ref('updated_at')
const sortOrder = ref('desc')
const viewMode = ref('list')
const selectedIndicators = ref([])

// 对话框状态
const showIndicatorDialog = ref(false)
const showHistoryDialog = ref(false)
const showImportDialog = ref(false)

// 表单数据
const indicatorForm = ref({
  name: '',
  category: '',
  description: '',
  tags: [],
  status: 'draft',
  code: ''
})

const editingIndicator = ref(null)
const saving = ref(false)
const importing = ref(false)

// 标签输入
const inputVisible = ref(false)
const inputValue = ref('')
const inputRef = ref(null)

// 版本历史
const versionHistory = ref([])

// 代码编辑器
const codeEditorRef = ref(null)
let codeEditor = null

// 分类配置
const categories = ref([
  { label: '趋势指标', value: 'trend' },
  { label: '震荡指标', value: 'oscillator' },
  { label: '成交量指标', value: 'volume' },
  { label: '动量指标', value: 'momentum' },
  { label: '波动率指标', value: 'volatility' },
  { label: '自定义指标', value: 'custom' }
])

// 表单验证规则
const indicatorRules = {
  name: [
    { required: true, message: '请输入指标名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  code: [
    { required: true, message: '请输入指标代码', trigger: 'blur' }
  ]
}

// 计算属性
const totalIndicators = computed(() => indicators.value.length)

const filteredIndicators = computed(() => {
  let result = indicators.value
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(indicator => 
      indicator.name.toLowerCase().includes(query) ||
      indicator.description?.toLowerCase().includes(query) ||
      indicator.tags?.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  // 分类过滤
  if (selectedCategory.value) {
    result = result.filter(indicator => indicator.category === selectedCategory.value)
  }
  
  // 状态过滤
  if (selectedStatus.value) {
    result = result.filter(indicator => indicator.status === selectedStatus.value)
  }
  
  // 排序
  result.sort((a, b) => {
    const aValue = a[sortBy.value]
    const bValue = b[sortBy.value]
    
    if (sortOrder.value === 'asc') {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })
  
  return result
})

// 组件挂载
onMounted(() => {
  loadIndicators()
})

// 监听器
watch(showIndicatorDialog, (visible) => {
  if (visible) {
    nextTick(() => {
      initCodeEditor()
    })
  } else {
    if (codeEditor) {
      codeEditor.dispose()
      codeEditor = null
    }
  }
})

// 加载指标列表
async function loadIndicators() {
  try {
    const response = await fetch('/api/indicators')
    if (response.ok) {
      indicators.value = await response.json()
    }
  } catch (error) {
    console.error('加载指标失败:', error)
    // 使用模拟数据
    indicators.value = generateMockData()
  }
}

// 生成模拟数据
function generateMockData() {
  return [
    {
      id: 1,
      name: '双均线交叉',
      description: '5日均线和20日均线交叉指标',
      category: 'trend',
      version: '1.0',
      status: 'published',
      usage_count: 25,
      is_favorite: true,
      tags: ['均线', '交叉', '趋势'],
      code: 'MA5:=MA(CLOSE,5);\nMA20:=MA(CLOSE,20);\n金叉:MA5>MA20 AND REF(MA5,1)<=REF(MA20,1);',
      created_at: new Date('2024-01-15'),
      updated_at: new Date('2024-01-20'),
      author: '系统'
    },
    {
      id: 2,
      name: 'MACD指标',
      description: '指数平滑异同移动平均线',
      category: 'momentum',
      version: '1.2',
      status: 'published',
      usage_count: 42,
      is_favorite: false,
      tags: ['MACD', '动量', '背离'],
      code: 'DIF:=EMA(CLOSE,12)-EMA(CLOSE,26);\nDEA:=EMA(DIF,9);\nMACD:=(DIF-DEA)*2;',
      created_at: new Date('2024-01-10'),
      updated_at: new Date('2024-01-18'),
      author: '系统'
    },
    {
      id: 3,
      name: 'RSI相对强弱',
      description: '相对强弱指标，判断超买超卖',
      category: 'oscillator',
      version: '1.0',
      status: 'draft',
      usage_count: 15,
      is_favorite: false,
      tags: ['RSI', '超买', '超卖'],
      code: 'LC:=REF(CLOSE,1);\nRSI:=SMA(MAX(CLOSE-LC,0),14,1)/SMA(ABS(CLOSE-LC),14,1)*100;',
      created_at: new Date('2024-01-12'),
      updated_at: new Date('2024-01-22'),
      author: '用户'
    }
  ]
}

// 搜索处理
function handleSearch() {
  // 搜索逻辑已在计算属性中处理
}

// 筛选处理
function handleFilter() {
  // 筛选逻辑已在计算属性中处理
}

// 排序处理
function handleSort() {
  // 排序逻辑已在计算属性中处理
}

// 切换排序顺序
function toggleSortOrder() {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

// 选择变化处理
function handleSelectionChange(selection) {
  selectedIndicators.value = selection
}

// 行点击处理
function handleRowClick(row) {
  editIndicator(row)
}

// 卡片点击处理
function handleCardClick(indicator) {
  editIndicator(indicator)
}

// 命令处理
function handleCommand({ action, row }) {
  switch (action) {
    case 'edit':
      editIndicator(row)
      break
    case 'duplicate':
      duplicateIndicator(row)
      break
    case 'export':
      exportIndicator(row)
      break
    case 'share':
      shareIndicator(row)
      break
    case 'history':
      showVersionHistory(row)
      break
    case 'archive':
      archiveIndicator(row)
      break
    case 'restore':
      restoreIndicator(row)
      break
    case 'delete':
      deleteIndicator(row)
      break
  }
}

// 创建新指标
function createNewIndicator() {
  editingIndicator.value = null
  resetIndicatorForm()
  showIndicatorDialog.value = true
}

// 编辑指标
function editIndicator(indicator) {
  editingIndicator.value = indicator
  indicatorForm.value = {
    name: indicator.name,
    category: indicator.category,
    description: indicator.description || '',
    tags: [...(indicator.tags || [])],
    status: indicator.status,
    code: indicator.code || ''
  }
  showIndicatorDialog.value = true
}

// 复制指标
function duplicateIndicator(indicator) {
  const newIndicator = {
    ...indicator,
    id: Date.now(),
    name: `${indicator.name} - 副本`,
    status: 'draft',
    usage_count: 0,
    is_favorite: false,
    created_at: new Date(),
    updated_at: new Date()
  }
  
  indicators.value.unshift(newIndicator)
  ElMessage.success('指标复制成功')
}

// 切换收藏
function toggleFavorite(indicator) {
  indicator.is_favorite = !indicator.is_favorite
  ElMessage.success(indicator.is_favorite ? '已添加到收藏' : '已取消收藏')
}

// 导出指标
function exportIndicator(indicator) {
  const data = {
    name: indicator.name,
    description: indicator.description,
    category: indicator.category,
    tags: indicator.tags,
    code: indicator.code,
    version: indicator.version,
    exported_at: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${indicator.name}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('指标导出成功')
}

// 分享指标
function shareIndicator(indicator) {
  const shareUrl = `${window.location.origin}/indicators/share/${indicator.id}`
  navigator.clipboard.writeText(shareUrl).then(() => {
    ElMessage.success('分享链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 显示版本历史
function showVersionHistory(indicator) {
  // 模拟版本历史数据
  versionHistory.value = [
    {
      id: 1,
      version: '1.2',
      author: '用户',
      changes: '优化了计算逻辑，提高了准确性',
      created_at: new Date('2024-01-20')
    },
    {
      id: 2,
      version: '1.1',
      author: '用户',
      changes: '修复了参数验证问题',
      created_at: new Date('2024-01-15')
    },
    {
      id: 3,
      version: '1.0',
      author: '系统',
      changes: '初始版本',
      created_at: new Date('2024-01-10')
    }
  ]
  
  showHistoryDialog.value = true
}

// 归档指标
function archiveIndicator(indicator) {
  ElMessageBox.confirm('确定要归档这个指标吗？', '确认归档', {
    type: 'warning'
  }).then(() => {
    indicator.status = 'archived'
    ElMessage.success('指标已归档')
  }).catch(() => {})
}

// 恢复指标
function restoreIndicator(indicator) {
  indicator.status = 'published'
  ElMessage.success('指标已恢复')
}

// 删除指标
function deleteIndicator(indicator) {
  ElMessageBox.confirm('确定要删除这个指标吗？此操作不可恢复。', '确认删除', {
    type: 'error'
  }).then(() => {
    const index = indicators.value.findIndex(item => item.id === indicator.id)
    if (index > -1) {
      indicators.value.splice(index, 1)
      ElMessage.success('指标已删除')
    }
  }).catch(() => {})
}

// 恢复版本
function restoreVersion(version) {
  ElMessageBox.confirm('确定要恢复到这个版本吗？', '确认恢复', {
    type: 'warning'
  }).then(() => {
    ElMessage.success('版本恢复成功')
    showHistoryDialog.value = false
  }).catch(() => {})
}

// 批量操作
function batchExport() {
  const data = selectedIndicators.value.map(indicator => ({
    name: indicator.name,
    description: indicator.description,
    category: indicator.category,
    tags: indicator.tags,
    code: indicator.code,
    version: indicator.version
  }))
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `indicators_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success(`已导出 ${selectedIndicators.value.length} 个指标`)
}

function batchFavorite() {
  selectedIndicators.value.forEach(indicator => {
    indicator.is_favorite = true
  })
  ElMessage.success(`已收藏 ${selectedIndicators.value.length} 个指标`)
}

function batchArchive() {
  ElMessageBox.confirm(`确定要归档选中的 ${selectedIndicators.value.length} 个指标吗？`, '确认归档', {
    type: 'warning'
  }).then(() => {
    selectedIndicators.value.forEach(indicator => {
      indicator.status = 'archived'
    })
    ElMessage.success(`已归档 ${selectedIndicators.value.length} 个指标`)
  }).catch(() => {})
}

function batchDelete() {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedIndicators.value.length} 个指标吗？此操作不可恢复。`, '确认删除', {
    type: 'error'
  }).then(() => {
    selectedIndicators.value.forEach(indicator => {
      const index = indicators.value.findIndex(item => item.id === indicator.id)
      if (index > -1) {
        indicators.value.splice(index, 1)
      }
    })
    ElMessage.success(`已删除 ${selectedIndicators.value.length} 个指标`)
    selectedIndicators.value = []
  }).catch(() => {})
}

// 导入指标
function importIndicators() {
  showImportDialog.value = true
}

function handleFileChange(file) {
  // 文件变化处理
}

function confirmImport() {
  importing.value = true
  
  // 模拟导入过程
  setTimeout(() => {
    importing.value = false
    showImportDialog.value = false
    ElMessage.success('指标导入成功')
    loadIndicators()
  }, 2000)
}

// 导出所有指标
function exportIndicators() {
  batchExport()
}

// 刷新指标
function refreshIndicators() {
  loadIndicators()
  ElMessage.success('指标列表已刷新')
}

// 保存指标
function saveIndicator() {
  // 表单验证
  // 这里应该调用表单验证方法
  
  saving.value = true
  
  // 获取代码编辑器内容
  if (codeEditor) {
    indicatorForm.value.code = codeEditor.getValue()
  }
  
  // 模拟保存过程
  setTimeout(() => {
    if (editingIndicator.value) {
      // 更新现有指标
      Object.assign(editingIndicator.value, {
        ...indicatorForm.value,
        updated_at: new Date()
      })
      ElMessage.success('指标更新成功')
    } else {
      // 创建新指标
      const newIndicator = {
        id: Date.now(),
        ...indicatorForm.value,
        version: '1.0',
        usage_count: 0,
        is_favorite: false,
        created_at: new Date(),
        updated_at: new Date(),
        author: '用户'
      }
      indicators.value.unshift(newIndicator)
      ElMessage.success('指标创建成功')
    }
    
    saving.value = false
    showIndicatorDialog.value = false
  }, 1000)
}

// 重置表单
function resetIndicatorForm() {
  indicatorForm.value = {
    name: '',
    category: '',
    description: '',
    tags: [],
    status: 'draft',
    code: ''
  }
  editingIndicator.value = null
}

// 标签操作
function removeTag(tag) {
  const index = indicatorForm.value.tags.indexOf(tag)
  if (index > -1) {
    indicatorForm.value.tags.splice(index, 1)
  }
}

function showInput() {
  inputVisible.value = true
  nextTick(() => {
    inputRef.value?.focus()
  })
}

function handleInputConfirm() {
  if (inputValue.value && !indicatorForm.value.tags.includes(inputValue.value)) {
    indicatorForm.value.tags.push(inputValue.value)
  }
  inputVisible.value = false
  inputValue.value = ''
}

// 初始化代码编辑器
function initCodeEditor() {
  if (codeEditorRef.value && !codeEditor) {
    codeEditor = monaco.editor.create(codeEditorRef.value, {
      value: indicatorForm.value.code,
      language: 'mai-lang',
      theme: 'vs',
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 14,
      lineNumbers: 'on',
      roundedSelection: false,
      automaticLayout: true
    })
  }
}

// 工具函数
function getIndicatorIcon(category) {
  const icons = {
    trend: 'TrendCharts',
    oscillator: 'DataAnalysis',
    volume: 'DataBoard',
    momentum: 'Lightning',
    volatility: 'Timer',
    custom: 'Setting'
  }
  return icons[category] || 'Document'
}

function getCategoryType(category) {
  const types = {
    trend: 'primary',
    oscillator: 'success',
    volume: 'warning',
    momentum: 'danger',
    volatility: 'info',
    custom: 'default'
  }
  return types[category] || 'default'
}

function getCategoryLabel(category) {
  const category_obj = categories.value.find(cat => cat.value === category)
  return category_obj ? category_obj.label : category
}

function getStatusType(status) {
  const types = {
    draft: 'info',
    published: 'success',
    archived: 'warning'
  }
  return types[status] || 'default'
}

function getStatusLabel(status) {
  const labels = {
    draft: '草稿',
    published: '已发布',
    archived: '已归档'
  }
  return labels[status] || status
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleString()
}
</script>

<style scoped>
.indicator-manager {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--tv-bg-secondary);
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.manager-icon {
  color: var(--tv-primary);
  font-size: 20px;
}

.manager-title {
  font-weight: 500;
  color: var(--tv-text-primary);
  font-size: 16px;
}

.search-filter {
  padding: 16px;
  border-bottom: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-secondary);
}

.search-bar {
  margin-bottom: 12px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.indicator-list {
  flex: 1;
  overflow: hidden;
}

.list-view {
  height: 100%;
  overflow-y: auto;
}

.indicator-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.indicator-icon {
  color: var(--tv-primary);
}

.card-view {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.indicator-card {
  border: 1px solid var(--tv-border-primary);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--tv-bg-secondary);
}

.indicator-card:hover {
  border-color: var(--tv-primary);
  box-shadow: 0 2px 8px var(--tv-shadow-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: var(--tv-text-primary);
}

.card-icon {
  color: var(--tv-primary);
}

.card-actions {
  display: flex;
  gap: 4px;
}

.card-content {
  margin-bottom: 12px;
}

.card-description {
  margin: 0 0 8px 0;
  color: var(--tv-text-secondary);
  font-size: 14px;
  line-height: 1.4;
}

.card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--tv-text-secondary);
}

.card-meta {
  display: flex;
  gap: 12px;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bottom-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid var(--tv-border-primary);
  background: var(--tv-bg-primary);
}

.view-toggle {
  position: absolute;
  top: 16px;
  right: 200px;
}

.code-editor-container {
  border: 1px solid var(--tv-border-primary);
  border-radius: 4px;
  overflow: hidden;
}

.code-editor {
  height: 200px;
}

.version-item {
  background: var(--tv-bg-primary);
  padding: 12px;
  border-radius: 4px;
  border: 1px solid var(--tv-border-primary);
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.version-number {
  font-weight: 500;
  color: var(--tv-primary);
}

.version-author {
  color: var(--tv-text-secondary);
  font-size: 12px;
}

.version-changes {
  color: var(--tv-text-secondary);
  font-size: 14px;
}
</style>