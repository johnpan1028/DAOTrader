# DAOTrader 期货数据管理器
# 整合AKShare接口调用和期货合约字典的统一数据管理系统

import akshare as ak
import pandas as pd
import logging
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from .futures_dictionary import (
    FuturesDictionary, FuturesContract, Exchange, Category, ContractType,
    get_futures_contract, get_akshare_symbol
)
from .akshare_client import AKShareClient


class FuturesDataManager:
    """期货数据管理器
    
    整合期货合约字典和AKShare数据接口，提供统一的期货数据获取服务
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.futures_dict = FuturesDictionary()
        self.akshare_client = AKShareClient()
        
        # AKShare期货数据接口映射
        self.akshare_interfaces = {
            'daily': 'futures_main_sina',  # 日线数据
            'realtime': 'futures_zh_realtime',  # 实时数据
            'contracts': 'futures_display_main_sina',  # 主力合约展示
            'delivery': 'futures_delivery_sina',  # 交割信息
        }
        
        self.logger.info("期货数据管理器初始化完成")
    
    def get_available_contracts(self) -> Dict[str, Dict]:
        """获取所有可用的期货合约信息"""
        return self.futures_dict.get_contract_info_dict()
    
    def get_contracts_by_exchange(self, exchange_name: str) -> List[Dict]:
        """按交易所获取合约列表"""
        try:
            exchange = Exchange(exchange_name)
            contracts = self.futures_dict.get_contracts_by_exchange(exchange)
            return [
                {
                    'symbol': contract.symbol,
                    'name': contract.name,
                    'category': contract.category.value,
                    'underlying': contract.underlying,
                    'unit': contract.unit,
                    'tick_size': contract.tick_size,
                    'has_night_trading': contract.has_night_trading,
                    'description': contract.description
                }
                for contract in contracts
            ]
        except ValueError:
            self.logger.error(f"未知的交易所: {exchange_name}")
            return []
    
    def get_contracts_by_category(self, category_name: str) -> List[Dict]:
        """按品种分类获取合约列表"""
        try:
            category = Category(category_name)
            contracts = self.futures_dict.get_contracts_by_category(category)
            return [
                {
                    'symbol': contract.symbol,
                    'name': contract.name,
                    'exchange': contract.exchange.value,
                    'underlying': contract.underlying,
                    'unit': contract.unit,
                    'tick_size': contract.tick_size,
                    'has_night_trading': contract.has_night_trading,
                    'description': contract.description
                }
                for contract in contracts
            ]
        except ValueError:
            self.logger.error(f"未知的品种分类: {category_name}")
            return []
    
    def search_contracts(self, keyword: str) -> List[Dict]:
        """搜索期货合约"""
        contracts = self.futures_dict.search_contracts(keyword)
        return [
            {
                'symbol': contract.symbol,
                'name': contract.name,
                'exchange': contract.exchange.value,
                'category': contract.category.value,
                'underlying': contract.underlying,
                'description': contract.description
            }
            for contract in contracts
        ]
    
    def get_contract_info(self, symbol: str) -> Optional[Dict]:
        """获取指定合约的详细信息"""
        contract = get_futures_contract(symbol)
        if not contract:
            return None
        
        return {
            'symbol': contract.symbol,
            'name': contract.name,
            'exchange': contract.exchange.value,
            'category': contract.category.value,
            'contract_type': contract.contract_type.value,
            'underlying': contract.underlying,
            'unit': contract.unit,
            'tick_size': contract.tick_size,
            'has_night_trading': contract.has_night_trading,
            'trading_hours': contract.trading_hours,
            'akshare_symbol': contract.akshare_symbol,
            'description': contract.description
        }
    
    def get_daily_data(self, symbol: str, start_date: str = None, 
                      end_date: str = None) -> Optional[pd.DataFrame]:
        """获取期货日线数据
        
        Args:
            symbol: 合约代码，如 'RB0'
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
        
        Returns:
            DataFrame: 包含日线数据的DataFrame，或None（如果获取失败）
        """
        # 验证合约是否存在
        contract = get_futures_contract(symbol)
        if not contract:
            self.logger.error(f"未找到合约: {symbol}")
            return None
        
        # 获取AKShare接口使用的代码
        akshare_symbol = contract.akshare_symbol
        
        try:
            # 使用现有的AKShareClient获取数据
            data = self.akshare_client.get_futures_data(
                symbol=akshare_symbol,
                period='1d',
                start_date=start_date,
                end_date=end_date
            )
            
            if data is not None and not data.empty:
                # 添加合约信息到数据中
                data['contract_name'] = contract.name
                data['exchange'] = contract.exchange.value
                data['category'] = contract.category.value
                
                self.logger.info(f"成功获取{symbol}日线数据，共{len(data)}条记录")
                return data
            else:
                self.logger.warning(f"未获取到{symbol}的数据")
                return None
                
        except Exception as e:
            self.logger.error(f"获取{symbol}日线数据失败: {str(e)}")
            return None
    
    def get_realtime_data(self, symbols: List[str] = None) -> Optional[pd.DataFrame]:
        """获取期货实时数据
        
        Args:
            symbols: 合约代码列表，如果为None则获取所有主力合约
        
        Returns:
            DataFrame: 包含实时数据的DataFrame
        """
        try:
            if symbols is None:
                # 获取所有主力合约
                all_contracts = self.futures_dict.get_all_contracts()
                symbols = [contract.symbol for contract in all_contracts 
                          if contract.contract_type == ContractType.MAIN]
            
            # 验证合约
            valid_symbols = []
            for symbol in symbols:
                if get_futures_contract(symbol):
                    valid_symbols.append(symbol)
                else:
                    self.logger.warning(f"跳过未知合约: {symbol}")
            
            if not valid_symbols:
                self.logger.error("没有有效的合约代码")
                return None
            
            # 获取实时数据（使用AKShare接口）
            realtime_data = ak.futures_zh_realtime()
            
            if realtime_data is not None and not realtime_data.empty:
                # 过滤指定合约的数据
                filtered_data = realtime_data[
                    realtime_data['代码'].isin(valid_symbols)
                ].copy()
                
                # 添加合约详细信息
                contract_info = []
                for _, row in filtered_data.iterrows():
                    contract = get_futures_contract(row['代码'])
                    if contract:
                        contract_info.append({
                            'contract_name': contract.name,
                            'exchange': contract.exchange.value,
                            'category': contract.category.value
                        })
                    else:
                        contract_info.append({
                            'contract_name': '',
                            'exchange': '',
                            'category': ''
                        })
                
                # 合并合约信息
                for i, info in enumerate(contract_info):
                    for key, value in info.items():
                        filtered_data.iloc[i, filtered_data.columns.get_loc(key) 
                                         if key in filtered_data.columns 
                                         else len(filtered_data.columns)] = value
                
                self.logger.info(f"成功获取{len(filtered_data)}个合约的实时数据")
                return filtered_data
            else:
                self.logger.warning("未获取到实时数据")
                return None
                
        except Exception as e:
            self.logger.error(f"获取实时数据失败: {str(e)}")
            return None
    
    def get_main_contracts_display(self) -> Optional[pd.DataFrame]:
        """获取主力合约展示数据"""
        try:
            display_data = ak.futures_display_main_sina()
            
            if display_data is not None and not display_data.empty:
                # 添加合约详细信息
                enhanced_data = display_data.copy()
                
                for idx, row in enhanced_data.iterrows():
                    symbol = row.get('symbol', '')
                    contract = get_futures_contract(symbol)
                    
                    if contract:
                        enhanced_data.loc[idx, 'contract_name'] = contract.name
                        enhanced_data.loc[idx, 'exchange'] = contract.exchange.value
                        enhanced_data.loc[idx, 'category'] = contract.category.value
                        enhanced_data.loc[idx, 'description'] = contract.description
                
                self.logger.info(f"成功获取主力合约展示数据，共{len(enhanced_data)}条记录")
                return enhanced_data
            else:
                self.logger.warning("未获取到主力合约展示数据")
                return None
                
        except Exception as e:
            self.logger.error(f"获取主力合约展示数据失败: {str(e)}")
            return None
    
    def validate_symbol(self, symbol: str) -> Tuple[bool, str]:
        """验证合约代码
        
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息或合约名称)
        """
        contract = get_futures_contract(symbol)
        if contract:
            return True, contract.name
        else:
            return False, f"未找到合约: {symbol}"
    
    def get_supported_exchanges(self) -> List[Dict[str, str]]:
        """获取支持的交易所列表"""
        return [
            {'code': exchange.name, 'name': exchange.value}
            for exchange in Exchange
        ]
    
    def get_supported_categories(self) -> List[Dict[str, str]]:
        """获取支持的品种分类列表"""
        return [
            {'code': category.name, 'name': category.value}
            for category in Category
        ]
    
    def get_contract_selection_data(self) -> Dict[str, any]:
        """获取合约选择数据（用于前端选择器）"""
        return {
            'exchanges': self.futures_dict.get_exchange_contracts_dict(),
            'categories': self.futures_dict.get_category_contracts_dict(),
            'all_contracts': [
                {
                    'symbol': contract.symbol,
                    'name': contract.name,
                    'exchange': contract.exchange.value,
                    'category': contract.category.value,
                    'description': contract.description
                }
                for contract in self.futures_dict.get_all_contracts()
            ],
            'exchange_list': self.get_supported_exchanges(),
            'category_list': self.get_supported_categories()
        }
    
    def batch_get_daily_data(self, symbols: List[str], start_date: str = None, 
                           end_date: str = None) -> Dict[str, pd.DataFrame]:
        """批量获取期货日线数据
        
        Args:
            symbols: 合约代码列表
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict[str, pd.DataFrame]: 合约代码为key，数据DataFrame为value的字典
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_daily_data(symbol, start_date, end_date)
                if data is not None:
                    results[symbol] = data
                else:
                    self.logger.warning(f"跳过无数据的合约: {symbol}")
            except Exception as e:
                self.logger.error(f"获取{symbol}数据失败: {str(e)}")
                continue
        
        self.logger.info(f"批量获取完成，成功获取{len(results)}个合约的数据")
        return results
    
    def validate_contract(self, symbol: str) -> bool:
        """验证合约代码是否有效"""
        try:
            contract = get_futures_contract(symbol)
            return contract is not None
        except Exception as e:
            self.logger.error(f"验证合约失败: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        try:
            all_contracts = self.futures_dict.get_all_contracts()
            stats = {
                'total_contracts': len(all_contracts),
                'exchanges': len(set(contract.exchange.value for contract in all_contracts)),
                'categories': len(set(contract.category.value for contract in all_contracts)),
                'night_trading_count': len([c for c in all_contracts if c.has_night_trading])
            }
            return stats
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {str(e)}")
            return {}
    
    def get_contract_statistics(self) -> Dict[str, int]:
        """获取合约统计信息"""
        all_contracts = self.futures_dict.get_all_contracts()
        
        stats = {
            'total_contracts': len(all_contracts),
            'exchanges': {},
            'categories': {},
            'night_trading_count': 0
        }
        
        for contract in all_contracts:
            # 按交易所统计
            exchange_name = contract.exchange.value
            stats['exchanges'][exchange_name] = stats['exchanges'].get(exchange_name, 0) + 1
            
            # 按品种分类统计
            category_name = contract.category.value
            stats['categories'][category_name] = stats['categories'].get(category_name, 0) + 1
            
            # 夜盘交易统计
            if contract.has_night_trading:
                stats['night_trading_count'] += 1
        
        return stats


# 全局实例
futures_data_manager = FuturesDataManager()


# 便捷函数
def get_futures_daily_data(symbol: str, start_date: str = None, 
                          end_date: str = None) -> Optional[pd.DataFrame]:
    """获取期货日线数据"""
    return futures_data_manager.get_daily_data(symbol, start_date, end_date)


def get_futures_realtime_data(symbols: List[str] = None) -> Optional[pd.DataFrame]:
    """获取期货实时数据"""
    return futures_data_manager.get_realtime_data(symbols)


def search_futures(keyword: str) -> List[Dict]:
    """搜索期货合约"""
    return futures_data_manager.search_contracts(keyword)


def get_contract_selection_data() -> Dict[str, any]:
    """获取合约选择数据"""
    return futures_data_manager.get_contract_selection_data()


# 创建全局实例
futures_manager = FuturesDataManager()