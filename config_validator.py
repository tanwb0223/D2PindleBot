"""
配置文件验证器
提供配置文件的验证和默认值设置
"""
import json
import logging
from typing import Dict, Any, List, Optional


class ConfigValidator:
    """配置文件验证器"""

    # 默认配置模板
    DEFAULT_CONFIG = {
        "game": {
            "window_title": "Diablo II: Resurrected"
        },
        "coordinates": {
            "lobby": {
                "create_game_button": [0, 0],
                "game_name_input": [0, 0],
                "game_password_input": [0, 0],
                "start_game_button": [0, 0]
            },
            "in_game": {
                "red_portal_position": [0, 0],
                "pindle_spawn_area": [0, 0],
                "legacy_pickup_positions": []
            },
            "teleport_path": [[0, 0], [0, 0], [0, 0]]
        },
        "bot": {
            "game_name": "pindlebot",
            "game_password": "",
            "runs_count": 100,
            "delay_between_runs": 1.2,
            "randomize_delays": True,
            "game_name_rotation": {
                "enabled": False,
                "names": ["pindle1", "pindle2", "pindle3"],
                "mode": "sequential",
                "change_every": 10,
                "add_random_suffix": False
            }
        },
        "pickup": {
            "item_types": ["unique", "rune"],
            "use_smart_pickup": True,
            "scan_area": [0, 0, 1920, 1080],
            "wait_for_corpse_explosion": True,
            "filter": {
                "pickup_all_runes": True,
                "pickup_all_uniques": True,
                "min_rune_level": None
            }
        },
        "sorceress": {
            "teleport_delay": 0.15,
            "cast_delay": 0.25,
            "static_field_casts": 3,
            "blizzard_casts": 3,
            "blizzard_delay": 0.6,
            "safety": {
                "teleport_away_after_cast": True,
                "safe_distance_x": 100,
                "safe_distance_y": -80,
                "wait_before_pickup": 1.5,
                "drink_potion_after_kill": True
            }
        },
        "hotkeys": {
            "static_field": "f2",
            "blizzard": "f1",
            "health_potion": "1",
            "mana_potion": "2"
        }
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_and_fix_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证并修复配置文件"""
        try:
            # 创建配置副本
            fixed_config = config.copy()

            # 验证并修复每个节
            for section_name, default_section in self.DEFAULT_CONFIG.items():
                if section_name not in fixed_config:
                    self.logger.warning(f"添加缺失的配置节: {section_name}")
                    fixed_config[section_name] = default_section.copy()
                else:
                    # 递归验证嵌套配置
                    fixed_config[section_name] = self._validate_section(
                        fixed_config[section_name],
                        default_section,
                        section_name
                    )

            # 验证特定类型的值
            self._validate_specific_values(fixed_config)

            return fixed_config

        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            raise

    def _validate_section(self, current_section: Dict[str, Any],
                         default_section: Dict[str, Any],
                         section_path: str) -> Dict[str, Any]:
        """验证配置节"""
        validated_section = current_section.copy()

        for key, default_value in default_section.items():
            if key not in validated_section:
                self.logger.warning(f"添加缺失的配置项: {section_path}.{key}")
                validated_section[key] = default_value
            elif isinstance(default_value, dict) and isinstance(validated_section[key], dict):
                # 递归验证嵌套字典
                validated_section[key] = self._validate_section(
                    validated_section[key],
                    default_value,
                    f"{section_path}.{key}"
                )

        return validated_section

    def _validate_specific_values(self, config: Dict[str, Any]) -> None:
        """验证特定类型的值"""
        try:
            # 验证坐标格式
            self._validate_coordinates(config.get('coordinates', {}))

            # 验证游戏名称长度
            game_name = config.get('bot', {}).get('game_name', '')
            if len(game_name) > 15:
                self.logger.warning("游戏名称过长，截断至15个字符")
                config['bot']['game_name'] = game_name[:15]

            # 验证运行次数
            runs_count = config.get('bot', {}).get('runs_count', 0)
            if not isinstance(runs_count, int) or runs_count <= 0:
                self.logger.warning("无效的运行次数，设置为默认值100")
                config['bot']['runs_count'] = 100

            # 验证延迟时间
            delay = config.get('bot', {}).get('delay_between_runs', 0)
            if not isinstance(delay, (int, float)) or delay < 0:
                self.logger.warning("无效的延迟时间，设置为默认值1.2秒")
                config['bot']['delay_between_runs'] = 1.2

        except Exception as e:
            self.logger.error(f"特定值验证失败: {e}")

    def _validate_coordinates(self, coordinates: Dict[str, Any]) -> None:
        """验证坐标格式"""
        try:
            # 验证大厅坐标
            lobby = coordinates.get('lobby', {})
            for coord_name, coord_value in lobby.items():
                if not self._is_valid_coordinate(coord_value):
                    self.logger.warning(f"无效的大厅坐标格式: {coord_name}")
                    lobby[coord_name] = [0, 0]

            # 验证游戏中坐标
            in_game = coordinates.get('in_game', {})
            for coord_name, coord_value in in_game.items():
                if coord_name == 'legacy_pickup_positions':
                    # 验证坐标列表
                    if not isinstance(coord_value, list):
                        self.logger.warning("legacy_pickup_positions 应该是列表格式")
                        in_game[coord_name] = []
                    elif not all(self._is_valid_coordinate(pos) for pos in coord_value):
                        self.logger.warning("legacy_pickup_positions 包含无效坐标")
                        in_game[coord_name] = []
                elif not self._is_valid_coordinate(coord_value):
                    self.logger.warning(f"无效的游戏中坐标格式: {coord_name}")
                    in_game[coord_name] = [0, 0]

            # 验证传送路径
            teleport_path = coordinates.get('teleport_path', [])
            if not isinstance(teleport_path, list) or len(teleport_path) == 0:
                self.logger.warning("传送路径为空，使用默认路径")
                coordinates['teleport_path'] = [[0, 0], [0, 0], [0, 0]]
            elif not all(self._is_valid_coordinate(point) for point in teleport_path):
                self.logger.warning("传送路径包含无效坐标")
                coordinates['teleport_path'] = [[0, 0], [0, 0], [0, 0]]

        except Exception as e:
            self.logger.error(f"坐标验证失败: {e}")

    def _is_valid_coordinate(self, coord: Any) -> bool:
        """检查坐标是否有效"""
        if not isinstance(coord, (list, tuple)) or len(coord) != 2:
            return False

        try:
            x, y = coord
            return isinstance(x, (int, float)) and isinstance(y, (int, float))
        except (ValueError, TypeError):
            return False

    def create_default_config(self, file_path: str) -> None:
        """创建默认配置文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
            self.logger.info(f"默认配置文件已创建: {file_path}")
        except Exception as e:
            self.logger.error(f"创建默认配置文件失败: {e}")
            raise

    def load_and_validate_config(self, file_path: str) -> Dict[str, Any]:
        """加载并验证配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            validated_config = self.validate_and_fix_config(config)
            self.logger.info("配置文件加载并验证成功")
            return validated_config

        except FileNotFoundError:
            self.logger.error(f"配置文件未找到: {file_path}")
            self.logger.info("正在创建默认配置文件...")
            self.create_default_config(file_path)
            return self.DEFAULT_CONFIG.copy()
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {e}")
            raise
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            raise