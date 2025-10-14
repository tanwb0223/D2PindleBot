import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
from typing import List, Tuple, Optional


class ItemDetector:
    """检测地面掉落物品（根据颜色识别）
    
    针对暗黑2重置版(D2R)优化
    """
    
    # 暗黑2重置版物品颜色范围 (BGR格式)
    # D2R使用更鲜艳的颜色和更好的渲染
    ITEM_COLORS = {
        'unique': {  # 暗金装备 - 深棕色文字
            'lower': np.array([0, 80, 160]),
            'upper': np.array([40, 150, 220])
        },
        'set': {  # 绿色套装 - 亮绿色
            'lower': np.array([40, 180, 40]),
            'upper': np.array([120, 255, 120])
        },
        'rare': {  # 稀有装备 - 黄色
            'lower': np.array([0, 180, 180]),
            'upper': np.array([80, 255, 255])
        },
        'magic': {  # 蓝色装备 - 蓝色
            'lower': np.array([180, 80, 20]),
            'upper': np.array([255, 180, 100])
        },
        'rune': {  # 符文 - 橙色/橙红色
            'lower': np.array([0, 120, 200]),
            'upper': np.array([60, 200, 255])
        },
        'gem_perfect': {  # 完美宝石 - 紫色
            'lower': np.array([120, 40, 120]),
            'upper': np.array([200, 100, 200])
        },
        'crafted': {  # 工艺物品 - 橙色
            'lower': np.array([0, 100, 180]),
            'upper': np.array([50, 180, 240])
        }
    }
    
    def __init__(self, hwnd: Optional[int] = None):
        self.hwnd = hwnd
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """截取屏幕
        
        Args:
            region: (x1, y1, x2, y2) 截取区域，None为全屏
            
        Returns:
            numpy数组格式的图像 (BGR)
        """
        if region:
            screenshot = ImageGrab.grab(bbox=region)
        else:
            screenshot = ImageGrab.grab()
        
        # 转换为OpenCV格式 (BGR)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return img
    
    def detect_items_by_color(self, 
                              img: np.ndarray, 
                              item_types: List[str] = ['unique'],
                              min_area: int = 30,
                              max_area: int = 5000) -> List[Tuple[int, int, str]]:
        """根据颜色检测物品位置（D2R优化版）
        
        Args:
            img: 图像数据
            item_types: 要检测的物品类型列表
            min_area: 最小检测区域（像素）
            max_area: 最大检测区域（像素）
            
        Returns:
            检测到的物品列表 [(x, y, item_type), ...]
        """
        positions = []
        
        # 转换到HSV色彩空间（对D2R更准确）
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        for item_type in item_types:
            if item_type not in self.ITEM_COLORS:
                continue
            
            color_range = self.ITEM_COLORS[item_type]
            
            # BGR颜色范围检测
            mask_bgr = cv2.inRange(img, color_range['lower'], color_range['upper'])
            
            # 增强对比度
            kernel_small = np.ones((3, 3), np.uint8)
            kernel_large = np.ones((5, 5), np.uint8)
            
            # 形态学处理 - 针对D2R优化
            mask = cv2.morphologyEx(mask_bgr, cv2.MORPH_CLOSE, kernel_small)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_small)
            mask = cv2.dilate(mask, kernel_large, iterations=1)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 筛选有效轮廓
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # D2R中物品名称文字较小，调整检测范围
                if min_area < area < max_area:
                    # 获取轮廓的边界框
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 宽高比检查（文字通常是横向的）
                    aspect_ratio = w / float(h) if h > 0 else 0
                    
                    # D2R物品名称通常宽度大于高度
                    if aspect_ratio > 0.3:  # 允许一些竖向物品
                        # 使用轮廓中心
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            positions.append((cx, cy, item_type))
        
        # 去除重复检测（同一位置可能被多种类型检测到）
        positions = self._remove_duplicates(positions, distance_threshold=20)
        
        return positions
    
    def _remove_duplicates(self, positions: List[Tuple[int, int, str]], 
                          distance_threshold: int = 20) -> List[Tuple[int, int, str]]:
        """移除距离过近的重复检测"""
        if not positions:
            return []
        
        filtered = []
        for pos in positions:
            is_duplicate = False
            for existing in filtered:
                dist = np.sqrt((pos[0] - existing[0])**2 + (pos[1] - existing[1])**2)
                if dist < distance_threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered.append(pos)
        
        return filtered
    
    def find_items_in_area(self, 
                          region: Tuple[int, int, int, int],
                          item_types: List[str] = ['unique']) -> List[Tuple[int, int, str]]:
        """在指定区域查找物品（D2R优化版）
        
        Args:
            region: (x1, y1, x2, y2) 搜索区域
            item_types: 物品类型列表
            
        Returns:
            物品的绝对屏幕坐标和类型 [(x, y, type), ...]
        """
        img = self.capture_screen(region)
        relative_positions = self.detect_items_by_color(img, item_types)
        
        # 转换为绝对坐标
        absolute_positions = [
            (region[0] + x, region[1] + y, item_type) 
            for x, y, item_type in relative_positions
        ]
        
        return absolute_positions
