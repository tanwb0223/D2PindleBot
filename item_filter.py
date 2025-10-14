"""
物品过滤器 - 判断是否拾取物品
根据符文等级和暗金装备价值过滤
"""
from typing import List, Dict


class ItemFilter:
    """物品过滤器"""
    
    # 符文等级表（从低到高）
    RUNE_LEVELS = {
        'El': 1, 'Eld': 2, 'Tir': 3, 'Nef': 4, 'Eth': 5, 'Ith': 6, 'Tal': 7, 'Ral': 8,
        'Ort': 9, 'Thul': 10, 'Amn': 11, 'Sol': 12, 'Shael': 13, 'Dol': 14, 'Hel': 15, 'Io': 16,
        'Lum': 17, 'Ko': 18, 'Fal': 19, 'Lem': 20, 'Pul': 21, 'Um': 22, 'Mal': 23, 'Ist': 24,
        'Gul': 25, 'Vex': 26, 'Ohm': 27, 'Lo': 28, 'Sur': 29, 'Ber': 30, 'Jah': 31, 'Cham': 32, 'Zod': 33
    }
    
    # Pindleskin常见高价值暗金装备
    HIGH_VALUE_UNIQUES = {
        # 头盔
        "Harlequin Crest": {"slot": "helm", "value": "很高"},
        "Vampire Gaze": {"slot": "helm", "value": "高"},
        "Andariel's Visage": {"slot": "helm", "value": "高"},
        "Crown of Ages": {"slot": "helm", "value": "很高"},
        
        # 武器
        "Windforce": {"slot": "bow", "value": "很高"},
        "Death's Fathom": {"slot": "orb", "value": "很高"},
        "Death's Web": {"slot": "wand", "value": "极高"},
        "Griffon's Eye": {"slot": "circlet", "value": "极高"},
        
        # 腰带
        "Arachnid Mesh": {"slot": "belt", "value": "很高"},
        "Thundergod's Vigor": {"slot": "belt", "value": "中"},
        
        # 靴子
        "War Traveler": {"slot": "boots", "value": "高"},
        "Sandstorm Trek": {"slot": "boots", "value": "中"},
        
        # 戒指/项链
        "Stones of Jordan": {"slot": "ring", "value": "极高"},
        "Mara's Kaleidoscope": {"slot": "amulet", "value": "很高"},
        "Highlord's Wrath": {"slot": "amulet", "value": "中"},
        
        # 护甲
        "Skin of the Vipermagi": {"slot": "armor", "value": "中"},
        "Ormus' Robes": {"slot": "armor", "value": "中"},
        "Tal Rasha's Guardianship": {"slot": "armor", "value": "高"},
        
        # 盾牌
        "Stormshield": {"slot": "shield", "value": "高"},
        "Herald of Zakarum": {"slot": "shield", "value": "中"},
        
        # 特殊物品
        "Annihilus": {"slot": "charm", "value": "极高"},
        "Hellfire Torch": {"slot": "charm", "value": "极高"},
        "Gheeds Fortune": {"slot": "charm", "value": "中"},
    }
    
    # 中低价值暗金装备（通常跳过）
    LOW_VALUE_UNIQUES = [
        "Tarnhelm", "Peasant Crown", "Wormskull",
        "Undead Crown", "Bloodrise", "The Gnasher",
        "Crushflange", "Bloodletter", "Coldsteel Eye",
        "Bladebone", "Skullder's Ire", "The Atlantean",
        "Crainte Vomir", "Bing Sz Wang", "The Vile Husk"
    ]
    
    def __init__(self, config: Dict):
        self.config = config
        self.filter_config = config.get('pickup', {}).get('filter', {})
        self.enabled = self.filter_config.get('enabled', True)
        
        # 符文设置
        self.pickup_all_runes = self.filter_config.get('pickup_all_runes', True)
        self.min_rune_level = self.filter_config.get('min_rune_level', 'Io')
        
        # 暗金装备设置（重要：未鉴定的暗金无法看到名称！）
        self.pickup_all_uniques = self.filter_config.get('pickup_all_uniques', True)
        self.filter_by_size = self.filter_config.get('filter_by_size', False)
        self.skip_small_items = self.filter_config.get('skip_small_items', False)
        self.skip_large_items = self.filter_config.get('skip_large_items', False)
    
    def should_pickup_rune(self, rune_name: str = None) -> bool:
        """判断是否拾取符文"""
        if not self.enabled:
            return True  # 过滤器禁用，拾取所有
        
        if self.pickup_all_runes:
            return True  # 拾取所有符文
        
        if rune_name and rune_name in self.RUNE_LEVELS:
            min_level = self.RUNE_LEVELS.get(self.min_rune_level, 16)
            rune_level = self.RUNE_LEVELS.get(rune_name, 0)
            return rune_level >= min_level
        
        # 如果无法识别符文名称，默认拾取
        return True
    
    def should_pickup_unique(self, item_size: int = None, item_name: str = None) -> bool:
        """判断是否拾取暗金装备
        
        重要说明：
        - D2R中的暗金装备掉落时是**未鉴定**状态
        - 未鉴定的装备只显示基础类型名称，无法看到实际是哪个暗金
        - 因此无法通过名称判断价值
        
        Args:
            item_size: 物品检测区域大小（像素）
            item_name: 物品名称（通常为None，因为未鉴定）
        
        Returns:
            是否拾取该物品
        """
        if not self.enabled:
            return True  # 过滤器禁用，拾取所有
        
        # 暗金装备在未鉴定时无法判断价值，默认全部拾取
        if self.pickup_all_uniques:
            return True
        
        # 高级功能：根据物品大小启发式过滤（不推荐，可能漏掉好东西）
        if self.filter_by_size and item_size:
            # 小物品（可能是戒指、项链、护身符）
            if self.skip_small_items and item_size < 100:
                return False
            # 大物品（可能是护甲、大型武器）
            if self.skip_large_items and item_size > 5000:
                return False
        
        # 默认拾取所有暗金
        return True
    
    def get_min_rune_level(self) -> int:
        """获取最低符文等级数值"""
        return self.RUNE_LEVELS.get(self.min_rune_level, 16)
    
    def is_high_value_unique(self, item_name: str) -> bool:
        """判断是否为高价值暗金"""
        return item_name in self.HIGH_VALUE_UNIQUES
    
    def get_item_value_tier(self, item_name: str) -> str:
        """获取物品价值等级"""
        if item_name in self.HIGH_VALUE_UNIQUES:
            return self.HIGH_VALUE_UNIQUES[item_name].get('value', '未知')
        if item_name in self.LOW_VALUE_UNIQUES:
            return '低'
        return '未知'
    
    def get_pickup_summary(self) -> Dict:
        """获取拾取策略摘要"""
        rune_strategy = "所有符文" if self.pickup_all_runes else f"≥{self.min_rune_level}"
        unique_strategy = "所有暗金" if self.pickup_all_uniques else "按大小过滤"
        
        return {
            "enabled": self.enabled,
            "runes": rune_strategy,
            "uniques": unique_strategy,
            "filter_by_size": self.filter_by_size
        }
