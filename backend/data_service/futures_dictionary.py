# DAOTrader 期货合约数据字典
# 基于AKShare期货数据接口的标准化合约映射系统

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Exchange(Enum):
    """期货交易所枚举"""
    SHFE = "上海期货交易所"  # 上期所
    INE = "上海国际能源交易中心"  # 能源中心
    DCE = "大连商品交易所"  # 大商所
    CZCE = "郑州商品交易所"  # 郑商所
    CFFEX = "中国金融期货交易所"  # 中金所
    GFEX = "广州期货交易所"  # 广期所


class ContractType(Enum):
    """合约类型枚举"""
    MAIN = "主力合约"  # 主力连续合约，如RB0
    INDEX = "指数合约"  # 指数连续合约，如RB000
    CONTINUOUS = "连续合约"  # 连续合约，如RB888
    SPECIFIC = "具体合约"  # 具体月份合约，如RB2501


class Category(Enum):
    """期货品种分类"""
    METAL = "金属"
    ENERGY = "能源化工"
    AGRICULTURE = "农产品"
    FINANCIAL = "金融"
    INDUSTRIAL = "工业品"


@dataclass
class FuturesContract:
    """期货合约信息"""
    symbol: str  # 合约代码，如 'RB0'
    name: str  # 合约名称，如 '螺纹钢主力'
    exchange: Exchange  # 交易所
    category: Category  # 品种分类
    contract_type: ContractType  # 合约类型
    underlying: str  # 标的品种代码，如 'rb'
    unit: str  # 交易单位
    tick_size: float  # 最小变动价位
    has_night_trading: bool  # 是否有夜盘
    trading_hours: Dict[str, str]  # 交易时间
    akshare_symbol: str  # AKShare接口使用的代码
    description: str = ""  # 描述信息


class FuturesDictionary:
    """期货合约数据字典"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._contracts: Dict[str, FuturesContract] = {}
        self._init_contracts()
    
    def _init_contracts(self):
        """初始化期货合约字典"""
        
        # 上海期货交易所 - 金属类
        metal_contracts = [
            # 螺纹钢
            FuturesContract(
                symbol="RB0", name="螺纹钢主力", exchange=Exchange.SHFE, 
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="rb", unit="10吨/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="RB0", description="建筑钢材，基础设施建设重要原料"
            ),
            # 热轧卷板
            FuturesContract(
                symbol="HC0", name="热轧卷板主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="hc", unit="10吨/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="HC0", description="热轧钢卷，制造业重要原料"
            ),
            # 铜
            FuturesContract(
                symbol="CU0", name="沪铜主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="cu", unit="5吨/手", tick_size=10.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-01:00"},
                akshare_symbol="CU0", description="工业金属之王，经济晴雨表"
            ),
            # 铝
            FuturesContract(
                symbol="AL0", name="沪铝主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="al", unit="5吨/手", tick_size=5.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-01:00"},
                akshare_symbol="AL0", description="轻金属，航空汽车工业重要材料"
            ),
            # 锌
            FuturesContract(
                symbol="ZN0", name="沪锌主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="zn", unit="5吨/手", tick_size=5.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-01:00"},
                akshare_symbol="ZN0", description="镀锌防腐重要金属"
            ),
            # 镍
            FuturesContract(
                symbol="NI0", name="沪镍主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="ni", unit="1吨/手", tick_size=10.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-01:00"},
                akshare_symbol="NI0", description="不锈钢重要原料，新能源电池材料"
            ),
            # 不锈钢
            FuturesContract(
                symbol="SS0", name="不锈钢主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="ss", unit="5吨/手", tick_size=5.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-01:00"},
                akshare_symbol="SS0", description="耐腐蚀钢材，高端制造业材料"
            ),
            # 黄金
            FuturesContract(
                symbol="AU0", name="沪金主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="au", unit="1000克/手", tick_size=0.02, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-02:30"},
                akshare_symbol="AU0", description="贵金属之王，避险资产"
            ),
            # 白银
            FuturesContract(
                symbol="AG0", name="沪银主力", exchange=Exchange.SHFE,
                category=Category.METAL, contract_type=ContractType.MAIN,
                underlying="ag", unit="15千克/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-02:30"},
                akshare_symbol="AG0", description="工业贵金属，投资避险双重属性"
            ),
        ]
        
        # 上海期货交易所 - 能源化工类
        energy_contracts = [
            # 原油
            FuturesContract(
                symbol="SC0", name="原油主力", exchange=Exchange.INE,
                category=Category.ENERGY, contract_type=ContractType.MAIN,
                underlying="sc", unit="1000桶/手", tick_size=0.1, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-02:30"},
                akshare_symbol="SC0", description="国际原油期货，能源之王"
            ),
            # 燃料油
            FuturesContract(
                symbol="FU0", name="燃料油主力", exchange=Exchange.SHFE,
                category=Category.ENERGY, contract_type=ContractType.MAIN,
                underlying="fu", unit="10吨/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="FU0", description="船用燃料，航运业重要成本"
            ),
            # 石油沥青
            FuturesContract(
                symbol="BU0", name="石油沥青主力", exchange=Exchange.SHFE,
                category=Category.ENERGY, contract_type=ContractType.MAIN,
                underlying="bu", unit="10吨/手", tick_size=2.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="BU0", description="道路建设重要材料"
            ),
        ]
        
        # 大连商品交易所 - 农产品类
        agriculture_contracts = [
            # 豆粕
            FuturesContract(
                symbol="M0", name="豆粕主力", exchange=Exchange.DCE,
                category=Category.AGRICULTURE, contract_type=ContractType.MAIN,
                underlying="m", unit="10吨/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="M0", description="饲料蛋白原料，养殖业重要成本"
            ),
            # 豆油
            FuturesContract(
                symbol="Y0", name="豆油主力", exchange=Exchange.DCE,
                category=Category.AGRICULTURE, contract_type=ContractType.MAIN,
                underlying="y", unit="10吨/手", tick_size=2.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="Y0", description="食用油重要品种"
            ),
            # 玉米
            FuturesContract(
                symbol="C0", name="玉米主力", exchange=Exchange.DCE,
                category=Category.AGRICULTURE, contract_type=ContractType.MAIN,
                underlying="c", unit="10吨/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="C0", description="饲料谷物，养殖业重要原料"
            ),
            # 棕榈油
            FuturesContract(
                symbol="P0", name="棕榈油主力", exchange=Exchange.DCE,
                category=Category.AGRICULTURE, contract_type=ContractType.MAIN,
                underlying="p", unit="10吨/手", tick_size=2.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="P0", description="热带植物油，食品工业原料"
            ),
        ]
        
        # 大连商品交易所 - 工业品类
        industrial_contracts = [
            # 铁矿石
            FuturesContract(
                symbol="I0", name="铁矿石主力", exchange=Exchange.DCE,
                category=Category.INDUSTRIAL, contract_type=ContractType.MAIN,
                underlying="i", unit="100吨/手", tick_size=0.5, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="I0", description="钢铁工业重要原料"
            ),
            # 焦炭
            FuturesContract(
                symbol="J0", name="焦炭主力", exchange=Exchange.DCE,
                category=Category.INDUSTRIAL, contract_type=ContractType.MAIN,
                underlying="j", unit="100吨/手", tick_size=0.5, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="J0", description="炼钢重要燃料"
            ),
            # 焦煤
            FuturesContract(
                symbol="JM0", name="焦煤主力", exchange=Exchange.DCE,
                category=Category.INDUSTRIAL, contract_type=ContractType.MAIN,
                underlying="jm", unit="60吨/手", tick_size=0.5, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="JM0", description="炼焦煤，钢铁工业原料"
            ),
        ]
        
        # 郑州商品交易所 - 农产品类
        czce_agriculture = [
            # 白糖
            FuturesContract(
                symbol="SR0", name="白糖主力", exchange=Exchange.CZCE,
                category=Category.AGRICULTURE, contract_type=ContractType.MAIN,
                underlying="SR", unit="10吨/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="SR0", description="食糖期货，食品工业重要原料"
            ),
            # 棉花
            FuturesContract(
                symbol="CF0", name="棉花主力", exchange=Exchange.CZCE,
                category=Category.AGRICULTURE, contract_type=ContractType.MAIN,
                underlying="CF", unit="5吨/手", tick_size=5.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="CF0", description="天然纤维，纺织工业原料"
            ),
        ]
        
        # 郑州商品交易所 - 化工类
        czce_chemical = [
            # PTA
            FuturesContract(
                symbol="TA0", name="PTA主力", exchange=Exchange.CZCE,
                category=Category.ENERGY, contract_type=ContractType.MAIN,
                underlying="TA", unit="5吨/手", tick_size=2.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="TA0", description="聚酯原料，化纤工业重要材料"
            ),
            # 甲醇
            FuturesContract(
                symbol="MA0", name="甲醇主力", exchange=Exchange.CZCE,
                category=Category.ENERGY, contract_type=ContractType.MAIN,
                underlying="MA", unit="10吨/手", tick_size=1.0, has_night_trading=True,
                trading_hours={"day": "09:00-15:00", "night": "21:00-23:00"},
                akshare_symbol="MA0", description="基础化工原料，新能源燃料"
            ),
        ]
        
        # 中国金融期货交易所 - 金融类
        financial_contracts = [
            # 沪深300股指
            FuturesContract(
                symbol="IF0", name="沪深300股指主力", exchange=Exchange.CFFEX,
                category=Category.FINANCIAL, contract_type=ContractType.MAIN,
                underlying="IF", unit="300元/点", tick_size=0.2, has_night_trading=False,
                trading_hours={"day": "09:30-15:00", "night": ""},
                akshare_symbol="IF0", description="A股市场重要指数期货"
            ),
            # 中证500股指
            FuturesContract(
                symbol="IC0", name="中证500股指主力", exchange=Exchange.CFFEX,
                category=Category.FINANCIAL, contract_type=ContractType.MAIN,
                underlying="IC", unit="200元/点", tick_size=0.2, has_night_trading=False,
                trading_hours={"day": "09:30-15:00", "night": ""},
                akshare_symbol="IC0", description="中小盘股指期货"
            ),
            # 上证50股指
            FuturesContract(
                symbol="IH0", name="上证50股指主力", exchange=Exchange.CFFEX,
                category=Category.FINANCIAL, contract_type=ContractType.MAIN,
                underlying="IH", unit="300元/点", tick_size=0.2, has_night_trading=False,
                trading_hours={"day": "09:30-15:00", "night": ""},
                akshare_symbol="IH0", description="大盘蓝筹股指期货"
            ),
        ]
        
        # 合并所有合约
        all_contracts = (
            metal_contracts + energy_contracts + agriculture_contracts + 
            industrial_contracts + czce_agriculture + czce_chemical + financial_contracts
        )
        
        # 添加到字典
        for contract in all_contracts:
            self._contracts[contract.symbol] = contract
        
        self.logger.info(f"初始化期货合约字典完成，共{len(self._contracts)}个合约")
    
    def get_contract(self, symbol: str) -> Optional[FuturesContract]:
        """获取期货合约信息"""
        return self._contracts.get(symbol.upper())
    
    def get_contracts_by_exchange(self, exchange: Exchange) -> List[FuturesContract]:
        """按交易所获取合约列表"""
        return [contract for contract in self._contracts.values() 
                if contract.exchange == exchange]
    
    def get_contracts_by_category(self, category: Category) -> List[FuturesContract]:
        """按品种分类获取合约列表"""
        return [contract for contract in self._contracts.values() 
                if contract.category == category]
    
    def get_all_contracts(self) -> List[FuturesContract]:
        """获取所有合约列表"""
        return list(self._contracts.values())
    
    def search_contracts(self, keyword: str) -> List[FuturesContract]:
        """搜索合约（按名称或代码）"""
        keyword = keyword.upper()
        results = []
        for contract in self._contracts.values():
            if (keyword in contract.symbol.upper() or 
                keyword in contract.name or 
                keyword in contract.underlying.upper()):
                results.append(contract)
        return results
    
    def get_akshare_symbol(self, symbol: str) -> Optional[str]:
        """获取AKShare接口使用的合约代码"""
        contract = self.get_contract(symbol)
        return contract.akshare_symbol if contract else None
    
    def get_contract_info_dict(self) -> Dict[str, Dict]:
        """获取合约信息字典（用于前端展示）"""
        result = {}
        for symbol, contract in self._contracts.items():
            result[symbol] = {
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
                'description': contract.description
            }
        return result
    
    def get_exchange_contracts_dict(self) -> Dict[str, List[Dict]]:
        """按交易所分组获取合约信息（用于前端选择器）"""
        result = {}
        for exchange in Exchange:
            contracts = self.get_contracts_by_exchange(exchange)
            result[exchange.value] = [
                {
                    'symbol': contract.symbol,
                    'name': contract.name,
                    'category': contract.category.value,
                    'description': contract.description
                }
                for contract in contracts
            ]
        return result
    
    def get_category_contracts_dict(self) -> Dict[str, List[Dict]]:
        """按品种分类分组获取合约信息（用于前端选择器）"""
        result = {}
        for category in Category:
            contracts = self.get_contracts_by_category(category)
            result[category.value] = [
                {
                    'symbol': contract.symbol,
                    'name': contract.name,
                    'exchange': contract.exchange.value,
                    'description': contract.description
                }
                for contract in contracts
            ]
        return result


# 全局实例
futures_dict = FuturesDictionary()


# 便捷函数
def get_futures_contract(symbol: str) -> Optional[FuturesContract]:
    """获取期货合约信息"""
    return futures_dict.get_contract(symbol)


def get_akshare_symbol(symbol: str) -> Optional[str]:
    """获取AKShare接口使用的合约代码"""
    return futures_dict.get_akshare_symbol(symbol)


def search_futures_contracts(keyword: str) -> List[FuturesContract]:
    """搜索期货合约"""
    return futures_dict.search_contracts(keyword)


def get_all_futures_contracts() -> List[FuturesContract]:
    """获取所有期货合约"""
    return futures_dict.get_all_contracts()