# DAOTrader 期货数据API接口
# 为前端提供期货合约选择和数据获取的RESTful API服务

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from data_service.futures_data_manager import (
    futures_manager,
    get_futures_daily_data,
    get_futures_realtime_data,
    search_futures,
    get_contract_selection_data
)
from data_service.futures_dictionary import (
    Exchange, Category, ContractType
)

# 创建蓝图
futures_bp = Blueprint('futures', __name__, url_prefix='/futures')
logger = logging.getLogger(__name__)


@futures_bp.route('/contracts', methods=['GET'])
@cross_origin()
def get_all_contracts():
    """获取所有期货合约信息"""
    try:
        contracts = futures_manager.get_available_contracts()
        return jsonify({
            'success': True,
            'data': contracts,
            'count': len(contracts),
            'message': '获取合约信息成功'
        })
    except Exception as e:
        logger.error(f"获取合约信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取合约信息失败'
        }), 500


@futures_bp.route('/contracts/selection', methods=['GET'])
@cross_origin()
def get_contract_selection():
    """获取合约选择数据（用于前端选择器组件）"""
    try:
        selection_data = futures_manager.get_contract_selection_data()
        return jsonify({
            'success': True,
            'data': selection_data,
            'message': '获取合约选择数据成功'
        })
    except Exception as e:
        logger.error(f"获取合约选择数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取合约选择数据失败'
        }), 500


@futures_bp.route('/contracts/exchange/<exchange_name>', methods=['GET'])
@cross_origin()
def get_contracts_by_exchange(exchange_name):
    """按交易所获取合约列表"""
    try:
        contracts = futures_manager.get_contracts_by_exchange(exchange_name)
        return jsonify({
            'success': True,
            'data': contracts,
            'count': len(contracts),
            'exchange': exchange_name,
            'message': f'获取{exchange_name}合约信息成功'
        })
    except Exception as e:
        logger.error(f"获取{exchange_name}合约信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'获取{exchange_name}合约信息失败'
        }), 500


@futures_bp.route('/contracts/category/<category_name>', methods=['GET'])
@cross_origin()
def get_contracts_by_category(category_name):
    """按品种分类获取合约列表"""
    try:
        contracts = futures_manager.get_contracts_by_category(category_name)
        return jsonify({
            'success': True,
            'data': contracts,
            'count': len(contracts),
            'category': category_name,
            'message': f'获取{category_name}类合约信息成功'
        })
    except Exception as e:
        logger.error(f"获取{category_name}类合约信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'获取{category_name}类合约信息失败'
        }), 500


@futures_bp.route('/contracts/search', methods=['GET'])
@cross_origin()
def search_contracts():
    """搜索期货合约"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空',
                'message': '请提供搜索关键词'
            }), 400
        
        contracts = search_futures(keyword)
        return jsonify({
            'success': True,
            'data': contracts,
            'count': len(contracts),
            'keyword': keyword,
            'message': f'搜索到{len(contracts)}个相关合约'
        })
    except Exception as e:
        logger.error(f"搜索合约失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '搜索合约失败'
        }), 500


@futures_bp.route('/contracts/<symbol>', methods=['GET'])
@cross_origin()
def get_contract_info(symbol):
    """获取指定合约的详细信息"""
    try:
        contract_info = futures_manager.get_contract_info(symbol.upper())
        if contract_info:
            return jsonify({
                'success': True,
                'data': contract_info,
                'message': f'获取{symbol}合约信息成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'未找到合约: {symbol}',
                'message': f'合约{symbol}不存在'
            }), 404
    except Exception as e:
        logger.error(f"获取{symbol}合约信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'获取{symbol}合约信息失败'
        }), 500


@futures_bp.route('/data/daily/<symbol>', methods=['GET'])
@cross_origin()
def get_daily_data(symbol):
    """获取期货日线数据"""
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        # 验证合约
        is_valid, message = futures_manager.validate_symbol(symbol.upper())
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message,
                'message': f'合约{symbol}无效'
            }), 400
        
        # 获取数据
        data = get_futures_daily_data(symbol.upper(), start_date, end_date)
        
        if data is not None and not data.empty:
            # 限制返回数据量
            if limit and limit > 0:
                data = data.tail(limit)
            
            # 转换为JSON格式
            data_dict = data.to_dict('records')
            
            return jsonify({
                'success': True,
                'data': data_dict,
                'count': len(data_dict),
                'symbol': symbol.upper(),
                'start_date': start_date,
                'end_date': end_date,
                'message': f'获取{symbol}日线数据成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '未获取到数据',
                'message': f'未找到{symbol}的日线数据'
            }), 404
            
    except Exception as e:
        logger.error(f"获取{symbol}日线数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'获取{symbol}日线数据失败'
        }), 500


@futures_bp.route('/data/realtime', methods=['GET'])
@cross_origin()
def get_realtime_data():
    """获取期货实时数据"""
    try:
        # 获取查询参数
        symbols_param = request.args.get('symbols')
        
        # 解析合约列表
        symbols = None
        if symbols_param:
            symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
        
        # 获取实时数据
        data = get_futures_realtime_data(symbols)
        
        if data is not None and not data.empty:
            # 转换为JSON格式
            data_dict = data.to_dict('records')
            
            return jsonify({
                'success': True,
                'data': data_dict,
                'count': len(data_dict),
                'symbols': symbols,
                'message': '获取实时数据成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '未获取到实时数据',
                'message': '实时数据获取失败'
            }), 404
            
    except Exception as e:
        logger.error(f"获取实时数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取实时数据失败'
        }), 500


@futures_bp.route('/data/batch', methods=['POST'])
@cross_origin()
def get_batch_daily_data():
    """批量获取期货日线数据"""
    try:
        # 获取请求数据
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                'success': False,
                'error': '请求数据不能为空',
                'message': '请提供有效的JSON数据'
            }), 400
        
        symbols = request_data.get('symbols', [])
        start_date = request_data.get('start_date')
        end_date = request_data.get('end_date')
        
        if not symbols:
            return jsonify({
                'success': False,
                'error': '合约列表不能为空',
                'message': '请提供要查询的合约列表'
            }), 400
        
        # 验证合约
        valid_symbols = []
        invalid_symbols = []
        
        for symbol in symbols:
            is_valid, _ = futures_manager.validate_symbol(symbol.upper())
            if is_valid:
                valid_symbols.append(symbol.upper())
            else:
                invalid_symbols.append(symbol)
        
        if not valid_symbols:
            return jsonify({
                'success': False,
                'error': '没有有效的合约代码',
                'invalid_symbols': invalid_symbols,
                'message': '所有提供的合约代码都无效'
            }), 400
        
        # 批量获取数据
        batch_data = futures_manager.batch_get_daily_data(
            valid_symbols, start_date, end_date
        )
        
        # 转换数据格式
        result_data = {}
        for symbol, df in batch_data.items():
            result_data[symbol] = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': result_data,
            'valid_symbols': valid_symbols,
            'invalid_symbols': invalid_symbols,
            'success_count': len(result_data),
            'start_date': start_date,
            'end_date': end_date,
            'message': f'批量获取完成，成功获取{len(result_data)}个合约的数据'
        })
        
    except Exception as e:
        logger.error(f"批量获取数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '批量获取数据失败'
        }), 500


@futures_bp.route('/exchanges', methods=['GET'])
@cross_origin()
def get_exchanges():
    """获取支持的交易所列表"""
    try:
        exchanges = futures_manager.get_supported_exchanges()
        return jsonify({
            'success': True,
            'data': exchanges,
            'count': len(exchanges),
            'message': '获取交易所列表成功'
        })
    except Exception as e:
        logger.error(f"获取交易所列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取交易所列表失败'
        }), 500


@futures_bp.route('/categories', methods=['GET'])
@cross_origin()
def get_categories():
    """获取支持的品种分类列表"""
    try:
        categories = futures_manager.get_supported_categories()
        return jsonify({
            'success': True,
            'data': categories,
            'count': len(categories),
            'message': '获取品种分类列表成功'
        })
    except Exception as e:
        logger.error(f"获取品种分类列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取品种分类列表失败'
        }), 500


@futures_bp.route('/statistics', methods=['GET'])
@cross_origin()
def get_statistics():
    """获取合约统计信息"""
    try:
        stats = futures_manager.get_contract_statistics()
        return jsonify({
            'success': True,
            'data': stats,
            'message': '获取统计信息成功'
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '获取统计信息失败'
        }), 500


@futures_bp.route('/validate/<symbol>', methods=['GET'])
@cross_origin()
def validate_contract(symbol):
    """验证合约代码"""
    try:
        is_valid, message = futures_manager.validate_symbol(symbol.upper())
        return jsonify({
            'success': True,
            'valid': is_valid,
            'symbol': symbol.upper(),
            'message': message
        })
    except Exception as e:
        logger.error(f"验证合约{symbol}失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'验证合约{symbol}失败'
        }), 500


# 错误处理
@futures_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'API接口不存在',
        'message': '请检查API路径是否正确'
    }), 404


@futures_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'HTTP方法不允许',
        'message': '请检查HTTP请求方法是否正确'
    }), 405


@futures_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误',
        'message': '请稍后重试或联系管理员'
    }), 500