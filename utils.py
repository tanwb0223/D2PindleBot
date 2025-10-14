"""
工具函数模块
包含随机延迟等辅助功能
"""
import random
import time


def random_delay(base_delay: float, variance: float = 0.2) -> float:
    """
    生成随机延迟时间
    
    Args:
        base_delay: 基础延迟时间（秒）
        variance: 变化范围（0-1之间，默认0.2即±20%）
    
    Returns:
        随机化后的延迟时间
    
    Example:
        >>> random_delay(1.0, 0.2)  # 返回0.8-1.2秒之间的随机值
        1.15
    """
    if variance <= 0:
        return base_delay
    
    min_delay = base_delay * (1 - variance)
    max_delay = base_delay * (1 + variance)
    return random.uniform(min_delay, max_delay)


def sleep_random(base_delay: float, variance: float = 0.2):
    """
    执行随机延迟等待
    
    Args:
        base_delay: 基础延迟时间（秒）
        variance: 变化范围（默认±20%）
    """
    delay = random_delay(base_delay, variance)
    time.sleep(delay)


def random_offset(base_coord: tuple, max_offset: int = 5) -> tuple:
    """
    为坐标添加随机偏移
    
    Args:
        base_coord: 基础坐标 (x, y)
        max_offset: 最大偏移像素（默认5像素）
    
    Returns:
        随机偏移后的坐标 (x, y)
    
    Example:
        >>> random_offset((960, 400), 5)
        (962, 398)
    """
    x, y = base_coord
    offset_x = random.randint(-max_offset, max_offset)
    offset_y = random.randint(-max_offset, max_offset)
    return (x + offset_x, y + offset_y)


def random_choice_weighted(choices: list, weights: list = None):
    """
    加权随机选择
    
    Args:
        choices: 选项列表
        weights: 权重列表（可选）
    
    Returns:
        随机选择的项
    """
    if weights is None:
        return random.choice(choices)
    return random.choices(choices, weights=weights, k=1)[0]
