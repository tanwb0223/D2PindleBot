import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
from typing import List, Tuple, Optional, Dict, Any
import logging
import time


class ItemDetector:
    """检测地面掉落物品（根据颜色识别）

    针对暗黑2重置版(D2R)优化
    """

    # 预定义的卷积核（避免重复创建）
    _KERNEL_SMALL = np.ones((3, 3), np.uint8)
    _KERNEL_LARGE = np.ones((5, 5), np.uint8)

    # 暗黑2重置版物品颜色范围 (BGR格式)
    # D2R使用更鲜艳的颜色和更好的渲染
    ITEM_COLORS: Dict[str, Dict[str, np.ndarray] = {
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
        self.logger = logging.getLogger(__name__)

        # 性能优化：缓存常用变量
        self._last_capture_time = 0
        self._capture_cooldown = 0.033  # 30 FPS限制
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """截取屏幕

        Args:
            region: (x1, y1, x2, y2) 截取区域，None为全屏

        Returns:
            numpy数组格式的图像 (BGR)
        """
        # 性能优化：限制截图频率
        current_time = time.time()
        if current_time - self._last_capture_time < self._capture_cooldown:
            time.sleep(self._capture_cooldown - (current_time - self._last_capture_time))

        self._last_capture_time = time.time()

        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()

            # 转换为OpenCV格式 (BGR)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return img
        except Exception as e:
            self.logger.error(f"屏幕截图失败: {e}")
            raise
    
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
        if img is None or img.size == 0:
            self.logger.warning("图像为空，跳过检测")
            return []

        positions = []

        # 输入验证
        if not item_types:
            self.logger.warning("未指定物品类型")
            return []

        # 性能优化：预先过滤无效的物品类型
        valid_item_types = [t for t in item_types if t in self.ITEM_COLORS]
        if not valid_item_types:
            self.logger.warning(f"无效的物品类型: {item_types}")
            return []

        for item_type in valid_item_types:
            try:
                color_range = self.ITEM_COLORS[item_type]

                # BGR颜色范围检测
                mask_bgr = cv2.inRange(img, color_range['lower'], color_range['upper'])

                # 性能优化：使用预定义的卷积核
                # 形态学处理 - 针对D2R优化
                mask = cv2.morphologyEx(mask_bgr, cv2.MORPH_CLOSE, self._KERNEL_SMALL)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self._KERNEL_SMALL)
                mask = cv2.dilate(mask, self._KERNEL_LARGE, iterations=1)

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

            except Exception as e:
                self.logger.error(f"检测物品类型 {item_type} 时出错: {e}")
                continue

        # 去除重复检测（同一位置可能被多种类型检测到）
        positions = self._remove_duplicates(positions, distance_threshold=20)

        return positions
    
    def _remove_duplicates(self, positions: List[Tuple[int, int, str]],
                          distance_threshold: int = 20) -> List[Tuple[int, int, str]]:
        """移除距离过近的重复检测

        Args:
            positions: 检测到的位置列表
            distance_threshold: 距离阈值（像素）

        Returns:
            过滤后的位置列表
        """
        if not positions:
            return []

        # 性能优化：使用更高效的去重算法
        filtered = []
        distance_squared = distance_threshold ** 2

        for pos in positions:
            is_duplicate = False
            for existing in filtered:
                # 性能优化：避免开方运算，比较平方距离
                dx = pos[0] - existing[0]
                dy = pos[1] - existing[1]
                dist_squared = dx * dx + dy * dy

                if dist_squared < distance_squared:
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
        # 输入验证
        if not isinstance(region, (tuple, list)) or len(region) != 4:
            raise ValueError(f"无效的区域格式: {region}")

        try:
            img = self.capture_screen(region)
            relative_positions = self.detect_items_by_color(img, item_types)

            # 转换为绝对坐标
            absolute_positions = [
                (region[0] + x, region[1] + y, item_type)
                for x, y, item_type in relative_positions
            ]

            return absolute_positions
        except Exception as e:
            self.logger.error(f"在区域 {region} 查找物品失败: {e}")
            return []
