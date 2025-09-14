from sqlalchemy import Column, Integer, String, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from ..database import Base


class IndicatorCategory(Base):
    """
    指标分类模型
    """
    __tablename__ = "indicator_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    value = Column(String(50), unique=True, index=True, nullable=False)
    label = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(20))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    indicators = relationship("Indicator", back_populates="category_obj")


class Indicator(Base):
    """
    指标模型
    """
    __tablename__ = "indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), ForeignKey("indicator_categories.value"), nullable=False)
    code = Column(Text, nullable=False)  # 麦语言代码
    compiled_code = Column(Text)  # 编译后的JavaScript代码
    parameters = Column(JSON, default=dict)  # 指标参数配置
    tags = Column(JSON, default=list)  # 标签列表
    version = Column(String(20), default="1.0")
    status = Column(String(20), default="draft")  # draft, published, archived
    
    # 使用统计
    usage_count = Column(Integer, default=0)
    is_favorite = Column(Boolean, default=False)
    
    # 验证状态
    is_validated = Column(Boolean, default=False)
    validation_errors = Column(JSON, default=list)
    
    # 性能指标
    avg_execution_time = Column(Integer, default=0)  # 平均执行时间(毫秒)
    memory_usage = Column(Integer, default=0)  # 内存使用量(KB)
    
    # 共享设置
    is_public = Column(Boolean, default=False)
    share_token = Column(String(100), unique=True, index=True)
    
    # 用户关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="indicators")
    category_obj = relationship("IndicatorCategory", back_populates="indicators")
    versions = relationship("IndicatorVersion", back_populates="indicator", cascade="all, delete-orphan")
    usage_logs = relationship("IndicatorUsageLog", back_populates="indicator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Indicator(id={self.id}, name='{self.name}', version='{self.version}')>"


class IndicatorVersion(Base):
    """
    指标版本历史模型
    """
    __tablename__ = "indicator_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    version = Column(String(20), nullable=False)
    code = Column(Text, nullable=False)
    compiled_code = Column(Text)
    parameters = Column(JSON, default=dict)
    changes = Column(Text)  # 版本变更说明
    
    # 版本统计
    usage_count = Column(Integer, default=0)
    
    # 创建信息
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    indicator = relationship("Indicator", back_populates="versions")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<IndicatorVersion(id={self.id}, indicator_id={self.indicator_id}, version='{self.version}')>"


class IndicatorUsageLog(Base):
    """
    指标使用日志模型
    """
    __tablename__ = "indicator_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 使用上下文
    context = Column(String(50))  # ide, backtest, live_trading
    session_id = Column(String(100))
    
    # 性能数据
    execution_time = Column(Integer)  # 执行时间(毫秒)
    memory_usage = Column(Integer)  # 内存使用量(KB)
    data_points = Column(Integer)  # 处理的数据点数量
    
    # 结果状态
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    indicator = relationship("Indicator", back_populates="usage_logs")
    user = relationship("User")
    
    def __repr__(self):
        return f"<IndicatorUsageLog(id={self.id}, indicator_id={self.indicator_id}, success={self.success})>"


class IndicatorTemplate(Base):
    """
    指标模板模型
    """
    __tablename__ = "indicator_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    
    # 模板内容
    template_code = Column(Text, nullable=False)
    parameters_schema = Column(JSON, default=dict)  # 参数配置模式
    
    # 模板属性
    difficulty_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    tags = Column(JSON, default=list)
    
    # 使用统计
    usage_count = Column(Integer, default=0)
    
    # 系统模板标识
    is_system = Column(Boolean, default=False)
    
    # 创建信息
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    creator = relationship("User")
    
    def __repr__(self):
        return f"<IndicatorTemplate(id={self.id}, name='{self.name}')>"


class IndicatorBacktest(Base):
    """
    指标回测结果模型
    """
    __tablename__ = "indicator_backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 回测配置
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # 回测参数
    parameters = Column(JSON, default=dict)
    
    # 回测结果
    total_signals = Column(Integer, default=0)
    profitable_signals = Column(Integer, default=0)
    win_rate = Column(Integer, default=0)  # 胜率百分比
    
    # 性能指标
    max_drawdown = Column(Integer, default=0)  # 最大回撤(基点)
    sharpe_ratio = Column(Integer, default=0)  # 夏普比率(放大100倍)
    
    # 执行信息
    execution_time = Column(Integer)  # 执行时间(毫秒)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    error_message = Column(Text)
    
    # 结果数据
    result_data = Column(JSON, default=dict)  # 详细回测结果
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # 关联关系
    indicator = relationship("Indicator")
    user = relationship("User")
    
    def __repr__(self):
        return f"<IndicatorBacktest(id={self.id}, indicator_id={self.indicator_id}, status='{self.status}')>"


class IndicatorAlert(Base):
    """
    指标预警模型
    """
    __tablename__ = "indicator_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 预警配置
    name = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    
    # 触发条件
    condition_type = Column(String(20), nullable=False)  # value, cross, divergence
    condition_config = Column(JSON, default=dict)
    
    # 通知设置
    notification_methods = Column(JSON, default=list)  # email, sms, webhook
    notification_config = Column(JSON, default=dict)
    
    # 状态管理
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    indicator = relationship("Indicator")
    user = relationship("User")
    
    def __repr__(self):
        return f"<IndicatorAlert(id={self.id}, name='{self.name}', is_active={self.is_active})>"