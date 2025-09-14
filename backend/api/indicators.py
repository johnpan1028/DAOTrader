from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import uuid
import asyncio
from pathlib import Path

from ..database import get_db
from ..models.user import User
from ..auth import get_current_user
from ..schemas.indicator import (
    IndicatorCreate, IndicatorUpdate, Indicator, IndicatorList,
    IndicatorCategoryCreate, IndicatorCategory, IndicatorSearch,
    IndicatorVersionCreate, IndicatorVersion, IndicatorUsageLogCreate,
    IndicatorTemplateCreate, IndicatorTemplate, IndicatorBacktestCreate,
    IndicatorAlertCreate, IndicatorAlert, IndicatorStats, IndicatorExport,
    IndicatorImport, IndicatorImportResult, IndicatorValidation, IndicatorCompile,
    IndicatorPerformance, IndicatorCategoryUpdate, IndicatorAlertUpdate
)
from ..models.indicator import (
    Indicator as IndicatorModel, IndicatorCategory as IndicatorCategoryModel,
    IndicatorVersion as IndicatorVersionModel, IndicatorUsageLog as IndicatorUsageLogModel,
    IndicatorTemplate as IndicatorTemplateModel, IndicatorBacktest as IndicatorBacktestModel,
    IndicatorAlert as IndicatorAlertModel
)

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("/", response_model=IndicatorList)
async def get_indicators(
    search: IndicatorSearch = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指标列表
    """
    query = db.query(IndicatorModel)
    
    # 用户过滤
    if search.user_id is None:
        query = query.filter(IndicatorModel.user_id == current_user.id)
    elif search.user_id != current_user.id:
        # 只能查看公开的指标
        query = query.filter(
            and_(
                IndicatorModel.user_id == search.user_id,
                IndicatorModel.is_public == True
            )
        )
    
    # 关键词搜索
    if search.keyword:
        query = query.filter(
            or_(
                IndicatorModel.name.contains(search.keyword),
                IndicatorModel.description.contains(search.keyword)
            )
        )
    
    # 分类过滤
    if search.category:
        query = query.filter(IndicatorModel.category == search.category)
    
    # 标签过滤
    if search.tags:
        for tag in search.tags:
            query = query.filter(IndicatorModel.tags.contains([tag]))
    
    # 状态过滤
    if search.status:
        query = query.filter(IndicatorModel.status == search.status)
    
    # 收藏过滤
    if search.is_favorite is not None:
        query = query.filter(IndicatorModel.is_favorite == search.is_favorite)
    
    # 公开状态过滤
    if search.is_public is not None:
        query = query.filter(IndicatorModel.is_public == search.is_public)
    
    # 排序
    if search.sort_by == "name":
        order_field = IndicatorModel.name
    elif search.sort_by == "created_at":
        order_field = IndicatorModel.created_at
    elif search.sort_by == "usage_count":
        order_field = IndicatorModel.usage_count
    else:
        order_field = IndicatorModel.updated_at
    
    if search.sort_order == "asc":
        query = query.order_by(asc(order_field))
    else:
        query = query.order_by(desc(order_field))
    
    # 分页
    total = query.count()
    indicators = query.offset((search.page - 1) * search.size).limit(search.size).all()
    
    return IndicatorList(
        items=indicators,
        total=total,
        page=search.page,
        size=search.size,
        pages=(total + search.size - 1) // search.size
    )


@router.get("/{indicator_id}", response_model=Indicator)
async def get_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定指标详情
    """
    indicator = db.query(IndicatorModel).filter(
        IndicatorModel.id == indicator_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 权限检查
    if indicator.user_id != current_user.id and not indicator.is_public:
        raise HTTPException(status_code=403, detail="无权访问此指标")
    
    # 增加使用计数
    if indicator.user_id != current_user.id:
        indicator.usage_count += 1
        db.commit()
    
    return indicator


@router.post("/", response_model=Indicator)
async def create_indicator(
    indicator_data: IndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新指标
    """
    try:
        # 检查名称是否重复
        existing = db.query(IndicatorModel).filter(
            and_(
                IndicatorModel.name == indicator_data.name,
                IndicatorModel.user_id == current_user.id
            )
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="指标名称已存在")
        
        # 创建指标
        indicator = IndicatorModel(
            **indicator_data.dict(),
            user_id=current_user.id,
            share_token=str(uuid.uuid4()) if indicator_data.is_public else None
        )
        
        db.add(indicator)
        db.commit()
        db.refresh(indicator)
        
        # 创建初始版本
        initial_version = IndicatorVersionModel(
            indicator_id=indicator.id,
            version=indicator_data.version,
            code=indicator_data.code,
            parameters=indicator_data.parameters,
            changes="初始版本",
            created_by=current_user.id
        )
        
        db.add(initial_version)
        db.commit()
        
        return indicator
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{indicator_id}", response_model=Indicator)
async def update_indicator(
    indicator_id: int,
    indicator_data: IndicatorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新指标
    """
    indicator = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.id == indicator_id,
            IndicatorModel.user_id == current_user.id
        )
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    try:
        # 检查名称重复
        if indicator_data.name and indicator_data.name != indicator.name:
            existing = db.query(IndicatorModel).filter(
                and_(
                    IndicatorModel.name == indicator_data.name,
                    IndicatorModel.user_id == current_user.id,
                    IndicatorModel.id != indicator_id
                )
            ).first()
            
            if existing:
                raise HTTPException(status_code=400, detail="指标名称已存在")
        
        # 更新指标字段
        update_data = indicator_data.dict(exclude_unset=True)
        old_code = indicator.code
        
        for field, value in update_data.items():
            setattr(indicator, field, value)
        
        indicator.updated_at = datetime.utcnow()
        
        # 如果代码有变化，创建新版本
        if indicator_data.code and indicator_data.code != old_code:
            new_version = IndicatorVersionModel(
                indicator_id=indicator.id,
                version=indicator_data.version or indicator.version,
                code=indicator_data.code,
                parameters=indicator_data.parameters or indicator.parameters,
                changes="代码更新",
                created_by=current_user.id
            )
            db.add(new_version)
        
        # 更新公开状态时生成或清除分享令牌
        if indicator_data.is_public is not None:
            if indicator_data.is_public and not indicator.share_token:
                indicator.share_token = str(uuid.uuid4())
            elif not indicator_data.is_public:
                indicator.share_token = None
        
        db.commit()
        db.refresh(indicator)
        
        return indicator
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{indicator_id}")
async def delete_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除指标
    """
    indicator = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.id == indicator_id,
            IndicatorModel.user_id == current_user.id
        )
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    try:
        # 删除相关版本记录
        db.query(IndicatorVersionModel).filter(
            IndicatorVersionModel.indicator_id == indicator_id
        ).delete()
        
        # 删除指标
        db.delete(indicator)
        db.commit()
        
        return {"message": "指标删除成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{indicator_id}/favorite")
async def toggle_favorite(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    切换指标收藏状态
    """
    indicator = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.id == indicator_id,
            IndicatorModel.user_id == current_user.id
        )
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    indicator.is_favorite = not indicator.is_favorite
    indicator.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "is_favorite": indicator.is_favorite,
        "message": "已添加到收藏" if indicator.is_favorite else "已取消收藏"
    }


@router.post("/{indicator_id}/duplicate")
async def duplicate_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    复制指标
    """
    original = db.query(IndicatorModel).filter(
        IndicatorModel.id == indicator_id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 权限检查
    if original.user_id != current_user.id and not original.is_public:
        raise HTTPException(status_code=403, detail="无权复制此指标")
    
    # 生成新名称
    base_name = f"{original.name} - 副本"
    counter = 1
    new_name = base_name
    
    while db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.name == new_name,
            IndicatorModel.user_id == current_user.id
        )
    ).first():
        counter += 1
        new_name = f"{base_name} ({counter})"
    
    # 创建副本
    duplicate = IndicatorModel(
        name=new_name,
        description=original.description,
        category=original.category,
        code=original.code,
        parameters=original.parameters,
        tags=original.tags,
        status="draft",
        user_id=current_user.id,
        version="1.0",
        usage_count=0,
        is_favorite=False,
        is_public=False,
        share_token=None
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    # 创建版本记录
    version = IndicatorVersionModel(
        indicator_id=duplicate.id,
        version="1.0",
        code=original.code,
        parameters=original.parameters,
        changes="从指标复制而来",
        created_by=current_user.id
    )
    
    db.add(version)
    db.commit()
    
    return duplicate


@router.get("/{indicator_id}/versions", response_model=List[IndicatorVersion])
async def get_indicator_versions(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指标版本历史
    """
    # 验证指标所有权
    indicator = db.query(IndicatorModel).filter(
        IndicatorModel.id == indicator_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 权限检查
    if indicator.user_id != current_user.id and not indicator.is_public:
        raise HTTPException(status_code=403, detail="无权访问此指标版本")
    
    versions = db.query(IndicatorVersionModel).filter(
        IndicatorVersionModel.indicator_id == indicator_id
    ).order_by(IndicatorVersionModel.created_at.desc()).all()
    
    return versions


@router.post("/{indicator_id}/versions/{version}/restore")
async def restore_version(
    indicator_id: int,
    version: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    恢复到指定版本
    """
    indicator = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.id == indicator_id,
            IndicatorModel.user_id == current_user.id
        )
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    version_record = db.query(IndicatorVersionModel).filter(
        and_(
            IndicatorVersionModel.indicator_id == indicator_id,
            IndicatorVersionModel.version == version
        )
    ).first()
    
    if not version_record:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    try:
        # 创建新版本记录
        version_parts = indicator.version.split('.')
        major = int(version_parts[0]) + 1
        new_version = f"{major}.0"
        
        new_version_record = IndicatorVersionModel(
            indicator_id=indicator.id,
            version=new_version,
            code=version_record.code,
            parameters=version_record.parameters,
            changes=f"恢复到版本 {version}",
            created_by=current_user.id
        )
        
        db.add(new_version_record)
        
        # 更新指标
        indicator.code = version_record.code
        indicator.parameters = version_record.parameters
        indicator.version = new_version
        indicator.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": f"已恢复到版本 {version}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import")
async def import_indicators(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导入指标
    """
    if not file.filename.endswith(('.json', '.mai')):
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    try:
        content = await file.read()
        
        if file.filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
        else:
            # 处理 .mai 格式文件
            data = parse_mai_file(content.decode('utf-8'))
        
        imported_count = 0
        
        # 支持单个指标或指标数组
        indicators_data = data if isinstance(data, list) else [data]
        
        for indicator_data in indicators_data:
            # 检查必要字段
            if not all(key in indicator_data for key in ['name', 'code']):
                continue
            
            # 生成唯一名称
            base_name = indicator_data['name']
            counter = 1
            new_name = base_name
            
            while db.query(IndicatorModel).filter(
                and_(
                    IndicatorModel.name == new_name,
                    IndicatorModel.user_id == current_user.id
                )
            ).first():
                counter += 1
                new_name = f"{base_name} ({counter})"
            
            # 创建指标
            indicator = IndicatorModel(
                name=new_name,
                description=indicator_data.get('description', ''),
                category=indicator_data.get('category', 'custom'),
                code=indicator_data['code'],
                parameters=indicator_data.get('parameters', {}),
                tags=indicator_data.get('tags', []),
                status='draft',
                user_id=current_user.id,
                version="1.0",
                is_public=False,
                share_token=None
            )
            
            db.add(indicator)
            db.flush()  # 获取 ID
            
            # 创建版本记录
            version = IndicatorVersionModel(
                indicator_id=indicator.id,
                version="1.0",
                code=indicator_data['code'],
                parameters=indicator_data.get('parameters', {}),
                changes="导入的指标",
                created_by=current_user.id
            )
            
            db.add(version)
            imported_count += 1
        
        db.commit()
        
        return {
            "message": f"成功导入 {imported_count} 个指标",
            "imported_count": imported_count
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="文件格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@router.get("/export/{indicator_id}")
async def export_indicator(
    indicator_id: int,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出指标
    """
    indicator = db.query(IndicatorModel).filter(
        IndicatorModel.id == indicator_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 权限检查
    if indicator.user_id != current_user.id and not indicator.is_public:
        raise HTTPException(status_code=403, detail="无权导出此指标")
    
    export_data = {
        "name": indicator.name,
        "description": indicator.description,
        "category": indicator.category,
        "code": indicator.code,
        "parameters": indicator.parameters,
        "tags": indicator.tags,
        "version": indicator.version,
        "exported_at": datetime.utcnow().isoformat()
    }
    
    if format == "mai":
        # 转换为麦语言格式
        return {
            "content": convert_to_mai_format(export_data),
            "filename": f"{indicator.name}.mai",
            "content_type": "text/plain"
        }
    else:
        return {
            "content": json.dumps(export_data, indent=2, ensure_ascii=False),
            "filename": f"{indicator.name}.json",
            "content_type": "application/json"
        }


@router.post("/batch/export")
async def batch_export_indicators(
    indicator_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量导出指标
    """
    indicators = db.query(IndicatorModel).filter(
        IndicatorModel.id.in_(indicator_ids)
    ).all()
    
    # 过滤权限
    accessible_indicators = [
        indicator for indicator in indicators
        if indicator.user_id == current_user.id or indicator.is_public
    ]
    
    if not accessible_indicators:
        raise HTTPException(status_code=404, detail="未找到可访问的指标")
    
    export_data = []
    for indicator in accessible_indicators:
        export_data.append({
            "name": indicator.name,
            "description": indicator.description,
            "category": indicator.category,
            "code": indicator.code,
            "parameters": indicator.parameters,
            "tags": indicator.tags,
            "version": indicator.version
        })
    
    return {
        "content": json.dumps(export_data, indent=2, ensure_ascii=False),
        "filename": f"indicators_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "content_type": "application/json"
    }


@router.get("/categories", response_model=List[IndicatorCategory])
async def get_categories(
    db: Session = Depends(get_db)
):
    """
    获取指标分类列表
    """
    categories = db.query(IndicatorCategoryModel).filter(
        IndicatorCategoryModel.is_active == True
    ).order_by(IndicatorCategoryModel.sort_order).all()
    
    # 如果数据库中没有分类，返回默认分类
    if not categories:
        default_categories = [
            {"value": "trend", "label": "趋势指标", "description": "用于判断价格趋势方向的指标", "sort_order": 1, "is_active": True},
            {"value": "oscillator", "label": "震荡指标", "description": "用于判断超买超卖的指标", "sort_order": 2, "is_active": True},
            {"value": "volume", "label": "成交量指标", "description": "基于成交量的技术指标", "sort_order": 3, "is_active": True},
            {"value": "momentum", "label": "动量指标", "description": "衡量价格变化速度的指标", "sort_order": 4, "is_active": True},
            {"value": "volatility", "label": "波动率指标", "description": "衡量价格波动程度的指标", "sort_order": 5, "is_active": True},
            {"value": "custom", "label": "自定义指标", "description": "用户自定义的指标", "sort_order": 6, "is_active": True}
        ]
        return default_categories
    
    return categories


@router.post("/categories", response_model=IndicatorCategory)
async def create_category(
    category: IndicatorCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建指标分类
    """
    # 检查分类是否已存在
    existing = db.query(IndicatorCategoryModel).filter(
        IndicatorCategoryModel.value == category.value
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="分类已存在")
    
    try:
        db_category = IndicatorCategoryModel(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates", response_model=List[IndicatorTemplate])
async def get_templates(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取指标模板列表
    """
    query = db.query(IndicatorTemplateModel).filter(
        IndicatorTemplateModel.is_active == True
    )
    
    if category:
        query = query.filter(IndicatorTemplateModel.category == category)
    
    templates = query.order_by(IndicatorTemplateModel.sort_order).all()
    return templates


@router.post("/templates", response_model=IndicatorTemplate)
async def create_template(
    template: IndicatorTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建指标模板
    """
    try:
        db_template = IndicatorTemplateModel(
            **template.dict(),
            created_by=current_user.id
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates/{template_id}", response_model=IndicatorTemplate)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定模板
    """
    template = db.query(IndicatorTemplateModel).filter(
        IndicatorTemplateModel.id == template_id,
        IndicatorTemplateModel.is_active == True
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    # 增加使用次数
    template.usage_count += 1
    db.commit()
    
    return template


@router.get("/stats/overview")
async def get_stats_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指标统计概览
    """
    # 总指标数
    total_indicators = db.query(IndicatorModel).filter(
        IndicatorModel.user_id == current_user.id
    ).count()
    
    # 活跃指标数
    active_indicators = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.user_id == current_user.id,
            IndicatorModel.status == "active"
        )
    ).count()
    
    # 收藏指标数
    favorite_indicators = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.user_id == current_user.id,
            IndicatorModel.is_favorite == True
        )
    ).count()
    
    # 公开指标数
    public_indicators = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.user_id == current_user.id,
            IndicatorModel.is_public == True
        )
    ).count()
    
    # 分类统计
    category_stats = db.query(
        IndicatorModel.category,
        func.count(IndicatorModel.id).label('count')
    ).filter(
        IndicatorModel.user_id == current_user.id
    ).group_by(IndicatorModel.category).all()
    
    # 最近使用的指标
    recent_indicators = db.query(IndicatorModel).filter(
        IndicatorModel.user_id == current_user.id
    ).order_by(IndicatorModel.updated_at.desc()).limit(5).all()
    
    return {
        "total_indicators": total_indicators,
        "active_indicators": active_indicators,
        "favorite_indicators": favorite_indicators,
        "public_indicators": public_indicators,
        "category_stats": [
            {"category": cat, "count": count} 
            for cat, count in category_stats
        ],
        "recent_indicators": recent_indicators
    }


@router.get("/shared/{share_token}", response_model=Indicator)
async def get_shared_indicator(
    share_token: str,
    db: Session = Depends(get_db)
):
    """
    通过分享令牌获取公开指标
    """
    indicator = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.share_token == share_token,
            IndicatorModel.is_public == True
        )
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="分享的指标不存在或已失效")
    
    # 增加使用计数
    indicator.usage_count += 1
    db.commit()
    
    return indicator


@router.post("/{indicator_id}/share")
async def share_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    分享指标（生成分享链接）
    """
    indicator = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.id == indicator_id,
            IndicatorModel.user_id == current_user.id
        )
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 设置为公开并生成分享令牌
    indicator.is_public = True
    if not indicator.share_token:
        indicator.share_token = str(uuid.uuid4())
    
    db.commit()
    
    return {
        "share_token": indicator.share_token,
        "share_url": f"/indicators/shared/{indicator.share_token}",
        "message": "指标分享成功"
    }


@router.delete("/{indicator_id}/share")
async def unshare_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消分享指标
    """
    indicator = db.query(IndicatorModel).filter(
        and_(
            IndicatorModel.id == indicator_id,
            IndicatorModel.user_id == current_user.id
        )
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 取消公开状态并清除分享令牌
    indicator.is_public = False
    indicator.share_token = None
    
    db.commit()
    
    return {"message": "已取消分享"}


@router.post("/{indicator_id}/usage")
async def increment_usage(
    indicator_id: int,
    usage_type: str = "execute",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    增加指标使用次数
    """
    indicator = db.query(IndicatorModel).filter(
        IndicatorModel.id == indicator_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 权限检查
    if indicator.user_id != current_user.id and not indicator.is_public:
        raise HTTPException(status_code=403, detail="无权使用此指标")
    
    # 记录使用日志
    usage_log = IndicatorUsageLogModel(
        indicator_id=indicator_id,
        user_id=current_user.id,
        usage_type=usage_type
    )
    db.add(usage_log)
    
    indicator.usage_count += 1
    indicator.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"usage_count": indicator.usage_count}


@router.post("/compile")
async def compile_indicator(
    code: str,
    parameters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    编译麦语言指标代码
    """
    try:
        # 这里应该调用麦语言编译器
        # 暂时返回模拟结果
        compiled_result = {
            "success": True,
            "javascript_code": f"// 编译后的JavaScript代码\n// 原始代码: {code[:50]}...",
            "vnpy_format": {
                "class_name": "CustomIndicator",
                "parameters": parameters or {},
                "lines": ["main"]
            },
            "klinechart_format": {
                "name": "custom_indicator",
                "calc": "function(dataList, indicator) { return []; }",
                "plots": [{"key": "main", "title": "Main", "type": "line"}]
            },
            "errors": [],
            "warnings": []
        }
        
        return compiled_result
    except Exception as e:
        return {
            "success": False,
            "javascript_code": "",
            "vnpy_format": {},
            "klinechart_format": {},
            "errors": [str(e)],
            "warnings": []
        }


@router.post("/validate")
async def validate_indicator(
    code: str,
    parameters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    验证指标代码和参数
    """
    try:
        # 这里应该调用指标验证器
        # 暂时返回模拟结果
        validation_result = {
            "is_valid": True,
            "syntax_errors": [],
            "runtime_errors": [],
            "warnings": [],
            "performance_score": 85,
            "compatibility": {
                "vnpy": True,
                "klinechart": True
            },
            "test_results": {
                "sample_data_points": 100,
                "execution_time_ms": 15.5,
                "memory_usage_mb": 2.1
            }
        }
        
        return validation_result
    except Exception as e:
        return {
            "is_valid": False,
            "syntax_errors": [str(e)],
            "runtime_errors": [],
            "warnings": [],
            "performance_score": 0,
            "compatibility": {"vnpy": False, "klinechart": False},
            "test_results": {}
        }


@router.post("/{indicator_id}/backtest")
async def run_backtest(
    indicator_id: int,
    symbol: str,
    timeframe: str,
    start_date: datetime,
    end_date: datetime,
    parameters: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    运行指标回测
    """
    indicator = db.query(IndicatorModel).filter(
        IndicatorModel.id == indicator_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 权限检查
    if indicator.user_id != current_user.id and not indicator.is_public:
        raise HTTPException(status_code=403, detail="无权回测此指标")
    
    try:
        # 创建回测记录
        backtest = IndicatorBacktestModel(
            indicator_id=indicator_id,
            user_id=current_user.id,
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            parameters=parameters,
            status="running"
        )
        
        db.add(backtest)
        db.commit()
        db.refresh(backtest)
        
        # 添加后台任务执行回测
        background_tasks.add_task(
            run_backtest_task,
            backtest.id,
            indicator.code,
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "start_date": start_date,
                "end_date": end_date,
                "parameters": parameters
            }
        )
        
        return backtest
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/backtests/{backtest_id}")
async def get_backtest_result(
    backtest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取回测结果
    """
    backtest = db.query(IndicatorBacktestModel).filter(
        and_(
            IndicatorBacktestModel.id == backtest_id,
            IndicatorBacktestModel.user_id == current_user.id
        )
    ).first()
    
    if not backtest:
        raise HTTPException(status_code=404, detail="回测记录不存在")
    
    return backtest


async def run_backtest_task(
    backtest_id: int,
    indicator_code: str,
    backtest_params: dict
):
    """
    执行回测的后台任务
    """
    # 这里应该实现实际的回测逻辑
    # 暂时模拟回测过程
    await asyncio.sleep(5)  # 模拟回测耗时
    
    # 更新回测结果
    from ..database import SessionLocal
    db = SessionLocal()
    
    try:
        backtest = db.query(IndicatorBacktestModel).filter(
            IndicatorBacktestModel.id == backtest_id
        ).first()
        
        if backtest:
            # 模拟回测结果
            backtest.status = "completed"
            backtest.results = {
                "total_return": 15.6,
                "sharpe_ratio": 1.25,
                "max_drawdown": -8.3,
                "win_rate": 0.65,
                "total_trades": 45,
                "profit_factor": 1.8
            }
            backtest.completed_at = datetime.utcnow()
            
            db.commit()
    except Exception as e:
        if backtest:
            backtest.status = "failed"
            backtest.error_message = str(e)
            db.commit()
    finally:
        db.close()


def parse_mai_file(content: str) -> dict:
    """
    解析麦语言文件格式
    """
    lines = content.strip().split('\n')
    
    # 简单的麦语言解析逻辑
    name = "导入的指标"
    description = ""
    code = content
    
    # 尝试从注释中提取名称和描述
    for line in lines:
        line = line.strip()
        if line.startswith('//') or line.startswith('{'):
            comment = line.lstrip('//').lstrip('{').rstrip('}').strip()
            if not name or name == "导入的指标":
                name = comment
            elif not description:
                description = comment
    
    return {
        "name": name,
        "description": description,
        "code": code,
        "category": "custom"
    }


def convert_to_mai_format(data: dict) -> str:
    """
    转换为麦语言格式
    """
    lines = []
    
    # 添加注释头
    lines.append(f"// {data['name']}")
    if data.get('description'):
        lines.append(f"// {data['description']}")
    lines.append(f"// 版本: {data['version']}")
    lines.append(f"// 导出时间: {data['exported_at']}")
    lines.append("")
    
    # 添加代码
    lines.append(data['code'])
    
    return '\n'.join(lines)