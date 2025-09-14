from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class IndicatorStatus(str, Enum):
    """指标状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ContextType(str, Enum):
    """使用上下文枚举"""
    IDE = "ide"
    BACKTEST = "backtest"
    LIVE_TRADING = "live_trading"


class ConditionType(str, Enum):
    """预警条件类型枚举"""
    VALUE = "value"
    CROSS = "cross"
    DIVERGENCE = "divergence"


class BacktestStatus(str, Enum):
    """回测状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ===== 指标分类相关 Schema =====

class IndicatorCategoryBase(BaseModel):
    """指标分类基础Schema"""
    value: str = Field(..., max_length=50, description="分类值")
    label: str = Field(..., max_length=100, description="分类标签")
    description: Optional[str] = Field(None, description="分类描述")
    icon: Optional[str] = Field(None, max_length=50, description="图标")
    color: Optional[str] = Field(None, max_length=20, description="颜色")
    sort_order: int = Field(0, description="排序")
    is_active: bool = Field(True, description="是否激活")


class IndicatorCategoryCreate(IndicatorCategoryBase):
    """创建指标分类Schema"""
    pass


class IndicatorCategoryUpdate(BaseModel):
    """更新指标分类Schema"""
    label: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class IndicatorCategory(IndicatorCategoryBase):
    """指标分类Schema"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== 指标相关 Schema =====

class IndicatorBase(BaseModel):
    """指标基础Schema"""
    name: str = Field(..., max_length=100, description="指标名称")
    description: Optional[str] = Field(None, description="指标描述")
    category: str = Field(..., max_length=50, description="指标分类")
    code: str = Field(..., description="麦语言代码")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数配置")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    version: str = Field("1.0", max_length=20, description="版本号")
    status: IndicatorStatus = Field(IndicatorStatus.DRAFT, description="状态")
    is_public: bool = Field(False, description="是否公开")


class IndicatorCreate(IndicatorBase):
    """创建指标Schema"""
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('指标名称不能为空')
        return v.strip()
    
    @validator('code')
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError('指标代码不能为空')
        return v.strip()


class IndicatorUpdate(BaseModel):
    """更新指标Schema"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    code: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    version: Optional[str] = Field(None, max_length=20)
    status: Optional[IndicatorStatus] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None


class IndicatorCompile(BaseModel):
    """编译指标Schema"""
    code: str = Field(..., description="麦语言代码")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数配置")
    validate_only: bool = Field(False, description="仅验证不保存")


class IndicatorValidation(BaseModel):
    """指标验证结果Schema"""
    is_valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
    compiled_code: Optional[str] = Field(None, description="编译后代码")
    execution_time: Optional[int] = Field(None, description="编译时间(毫秒)")


class Indicator(IndicatorBase):
    """指标Schema"""
    id: int
    compiled_code: Optional[str] = None
    usage_count: int = 0
    is_favorite: bool = False
    is_validated: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    avg_execution_time: int = 0
    memory_usage: int = 0
    share_token: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IndicatorList(BaseModel):
    """指标列表Schema"""
    items: List[Indicator]
    total: int
    page: int
    size: int
    pages: int


class IndicatorSearch(BaseModel):
    """指标搜索Schema"""
    keyword: Optional[str] = Field(None, description="关键词")
    category: Optional[str] = Field(None, description="分类")
    tags: Optional[List[str]] = Field(None, description="标签")
    status: Optional[IndicatorStatus] = Field(None, description="状态")
    is_favorite: Optional[bool] = Field(None, description="是否收藏")
    is_public: Optional[bool] = Field(None, description="是否公开")
    user_id: Optional[int] = Field(None, description="用户ID")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    sort_by: str = Field("updated_at", description="排序字段")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="排序方向")


# ===== 指标版本相关 Schema =====

class IndicatorVersionBase(BaseModel):
    """指标版本基础Schema"""
    version: str = Field(..., max_length=20, description="版本号")
    code: str = Field(..., description="代码")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数配置")
    changes: Optional[str] = Field(None, description="变更说明")


class IndicatorVersionCreate(IndicatorVersionBase):
    """创建指标版本Schema"""
    indicator_id: int = Field(..., description="指标ID")


class IndicatorVersion(IndicatorVersionBase):
    """指标版本Schema"""
    id: int
    indicator_id: int
    compiled_code: Optional[str] = None
    usage_count: int = 0
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== 指标使用日志相关 Schema =====

class IndicatorUsageLogCreate(BaseModel):
    """创建使用日志Schema"""
    indicator_id: int = Field(..., description="指标ID")
    context: ContextType = Field(..., description="使用上下文")
    session_id: Optional[str] = Field(None, max_length=100, description="会话ID")
    execution_time: Optional[int] = Field(None, description="执行时间")
    memory_usage: Optional[int] = Field(None, description="内存使用")
    data_points: Optional[int] = Field(None, description="数据点数")
    success: bool = Field(True, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")


class IndicatorUsageLog(BaseModel):
    """使用日志Schema"""
    id: int
    indicator_id: int
    user_id: int
    context: str
    session_id: Optional[str] = None
    execution_time: Optional[int] = None
    memory_usage: Optional[int] = None
    data_points: Optional[int] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== 指标模板相关 Schema =====

class IndicatorTemplateBase(BaseModel):
    """指标模板基础Schema"""
    name: str = Field(..., max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    category: str = Field(..., max_length=50, description="模板分类")
    template_code: str = Field(..., description="模板代码")
    parameters_schema: Dict[str, Any] = Field(default_factory=dict, description="参数模式")
    difficulty_level: DifficultyLevel = Field(DifficultyLevel.BEGINNER, description="难度等级")
    tags: List[str] = Field(default_factory=list, description="标签")


class IndicatorTemplateCreate(IndicatorTemplateBase):
    """创建指标模板Schema"""
    pass


class IndicatorTemplate(IndicatorTemplateBase):
    """指标模板Schema"""
    id: int
    usage_count: int = 0
    is_system: bool = False
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== 指标回测相关 Schema =====

class IndicatorBacktestBase(BaseModel):
    """指标回测基础Schema"""
    indicator_id: int = Field(..., description="指标ID")
    symbol: str = Field(..., max_length=20, description="交易品种")
    timeframe: str = Field(..., max_length=10, description="时间周期")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="回测参数")


class IndicatorBacktestCreate(IndicatorBacktestBase):
    """创建指标回测Schema"""
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('结束日期必须大于开始日期')
        return v


class IndicatorBacktest(IndicatorBacktestBase):
    """指标回测Schema"""
    id: int
    user_id: int
    total_signals: int = 0
    profitable_signals: int = 0
    win_rate: int = 0
    max_drawdown: int = 0
    sharpe_ratio: int = 0
    execution_time: Optional[int] = None
    status: BacktestStatus = BacktestStatus.PENDING
    error_message: Optional[str] = None
    result_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ===== 指标预警相关 Schema =====

class IndicatorAlertBase(BaseModel):
    """指标预警基础Schema"""
    indicator_id: int = Field(..., description="指标ID")
    name: str = Field(..., max_length=100, description="预警名称")
    symbol: str = Field(..., max_length=20, description="交易品种")
    timeframe: str = Field(..., max_length=10, description="时间周期")
    condition_type: ConditionType = Field(..., description="条件类型")
    condition_config: Dict[str, Any] = Field(default_factory=dict, description="条件配置")
    notification_methods: List[str] = Field(default_factory=list, description="通知方式")
    notification_config: Dict[str, Any] = Field(default_factory=dict, description="通知配置")
    is_active: bool = Field(True, description="是否激活")


class IndicatorAlertCreate(IndicatorAlertBase):
    """创建指标预警Schema"""
    pass


class IndicatorAlertUpdate(BaseModel):
    """更新指标预警Schema"""
    name: Optional[str] = Field(None, max_length=100)
    condition_config: Optional[Dict[str, Any]] = None
    notification_methods: Optional[List[str]] = None
    notification_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class IndicatorAlert(IndicatorAlertBase):
    """指标预警Schema"""
    id: int
    user_id: int
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ===== 统计和分析相关 Schema =====

class IndicatorStats(BaseModel):
    """指标统计Schema"""
    total_indicators: int = Field(..., description="指标总数")
    published_indicators: int = Field(..., description="已发布指标数")
    draft_indicators: int = Field(..., description="草稿指标数")
    favorite_indicators: int = Field(..., description="收藏指标数")
    total_usage: int = Field(..., description="总使用次数")
    avg_execution_time: float = Field(..., description="平均执行时间")
    categories_distribution: Dict[str, int] = Field(..., description="分类分布")
    tags_distribution: Dict[str, int] = Field(..., description="标签分布")
    recent_activity: List[Dict[str, Any]] = Field(..., description="最近活动")


class IndicatorPerformance(BaseModel):
    """指标性能Schema"""
    indicator_id: int = Field(..., description="指标ID")
    avg_execution_time: float = Field(..., description="平均执行时间")
    memory_usage: float = Field(..., description="内存使用量")
    success_rate: float = Field(..., description="成功率")
    usage_trend: List[Dict[str, Any]] = Field(..., description="使用趋势")
    error_distribution: Dict[str, int] = Field(..., description="错误分布")


# ===== 导入导出相关 Schema =====

class IndicatorExport(BaseModel):
    """指标导出Schema"""
    indicators: List[Indicator] = Field(..., description="指标列表")
    categories: List[IndicatorCategory] = Field(..., description="分类列表")
    templates: List[IndicatorTemplate] = Field(..., description="模板列表")
    export_time: datetime = Field(..., description="导出时间")
    version: str = Field("1.0", description="导出格式版本")


class IndicatorImport(BaseModel):
    """指标导入Schema"""
    file_content: str = Field(..., description="文件内容")
    overwrite_existing: bool = Field(False, description="是否覆盖已存在")
    import_categories: bool = Field(True, description="是否导入分类")
    import_templates: bool = Field(True, description="是否导入模板")


class IndicatorImportResult(BaseModel):
    """指标导入结果Schema"""
    success: bool = Field(..., description="是否成功")
    imported_indicators: int = Field(0, description="导入指标数")
    imported_categories: int = Field(0, description="导入分类数")
    imported_templates: int = Field(0, description="导入模板数")
    skipped_items: int = Field(0, description="跳过项目数")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")