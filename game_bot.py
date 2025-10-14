import json
import time
import logging
import random
from typing import Dict, Any, List
from window_controller import WindowController
from input_controller import InputController
from item_detector import ItemDetector
from item_filter import ItemFilter
from utils import random_delay, sleep_random, random_offset


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class D2PindleBot:
    def __init__(self, config_path: str = 'config.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config: Dict[str, Any] = json.load(f)
        
        self.window_controller = WindowController(self.config['game']['window_title'])
        self.input_controller = InputController()
        self.item_detector = ItemDetector()
        self.item_filter = ItemFilter(self.config)
        self.logger = logging.getLogger(__name__)
        self.run_count = 0
        self.is_running = False
        
        # 随机化设置
        self.randomize = self.config.get('bot', {}).get('randomize_delays', True)
        
        # 游戏名称轮换
        self.game_name_rotation = self.config.get('bot', {}).get('game_name_rotation', {})
        self.current_name_index = 0
        
        # 打印拾取策略
        pickup_summary = self.item_filter.get_pickup_summary()
        self.logger.info(f"拾取策略: 符文={pickup_summary['runes']}, "
                        f"暗金={pickup_summary['uniques']}")
    
    def initialize(self) -> bool:
        self.logger.info("正在初始化机器人...")
        if not self.window_controller.find_window():
            self.logger.error(f"未找到游戏窗口: {self.config['game']['window_title']}")
            return False
        
        if not self.window_controller.activate_window():
            self.logger.error("无法激活游戏窗口")
            return False
        
        self.logger.info("机器人初始化成功")
        return True
    
    def get_current_game_name(self) -> str:
        """获取当前应使用的游戏名称"""
        rotation_config = self.game_name_rotation
        
        if not rotation_config.get('enabled', False):
            # 未启用轮换，使用固定名称
            return self.config['bot']['game_name']
        
        names = rotation_config.get('names', [])
        if not names:
            return self.config['bot']['game_name']
        
        mode = rotation_config.get('mode', 'sequential')
        change_every = rotation_config.get('change_every', 10)
        add_suffix = rotation_config.get('add_random_suffix', False)
        
        # 计算当前应使用的名称索引
        if mode == 'sequential':
            # 顺序轮换
            self.current_name_index = (self.run_count // change_every) % len(names)
        elif mode == 'random':
            # 随机选择
            if self.run_count % change_every == 0:
                self.current_name_index = random.randint(0, len(names) - 1)
        
        base_name = names[self.current_name_index]
        
        # 添加随机后缀（可选）
        if add_suffix:
            suffix = random.randint(100, 999)
            return f"{base_name}{suffix}"
        
        return base_name
    
    def create_game(self):
        # 获取游戏名称
        game_name = self.get_current_game_name()
        self.logger.info(f"创建游戏: {game_name}...")
        
        lobby = self.config['coordinates']['lobby']
        
        # 点击创建游戏（随机偏移）
        coord = random_offset(lobby['create_game_button'], 3) if self.randomize else lobby['create_game_button']
        self.input_controller.click(*coord)
        sleep_random(1.0, 0.15) if self.randomize else time.sleep(1)
        
        # 输入游戏名称
        coord = random_offset(lobby['game_name_input'], 3) if self.randomize else lobby['game_name_input']
        self.input_controller.click(*coord)
        sleep_random(0.2, 0.3) if self.randomize else time.sleep(0.2)
        self.input_controller.type_text(game_name)
        
        # 输入密码（如果有）
        password = self.config['bot'].get('game_password', '')
        if password:
            coord = random_offset(lobby['game_password_input'], 3) if self.randomize else lobby['game_password_input']
            self.input_controller.click(*coord)
            sleep_random(0.2, 0.3) if self.randomize else time.sleep(0.2)
            self.input_controller.type_text(password)
        
        # 开始游戏
        coord = random_offset(lobby['start_game_button'], 3) if self.randomize else lobby['start_game_button']
        self.input_controller.click(*coord)
        sleep_random(5.0, 0.1) if self.randomize else time.sleep(5)
        
        self.logger.info("游戏创建完成")
    
    def navigate_to_red_portal(self):
        """从城镇初始位置导航到红门"""
        self.logger.info("从城镇导航到红门...")
        coords = self.config['coordinates']
        in_game = coords['in_game']
        
        # 获取城镇到红门的路径
        town_path = coords.get('town_to_portal_path', [])
        
        if town_path:
            # 使用预设路径传送
            self.logger.info(f"使用预设路径（{len(town_path)}个点）")
            for i, point in enumerate(town_path):
                coord = random_offset(point, 5) if self.randomize else point
                self.input_controller.click(*coord, button='right')
                
                delay = 0.4 if i == 0 else 0.3  # 第一次稍慢
                sleep_random(delay, 0.2) if self.randomize else time.sleep(delay)
        else:
            # 备用：直接尝试传送到红门附近
            self.logger.info("使用直接传送（备用）")
            portal_pos = in_game['red_portal_position']
            
            # 尝试多次传送靠近红门
            for attempt in range(3):
                # 随机偏移传送点，避免被卡
                offset = random.randint(10, 30)
                target_x = portal_pos[0] + offset
                target_y = portal_pos[1] + offset
                
                coord = random_offset((target_x, target_y), 8) if self.randomize else (target_x, target_y)
                self.input_controller.click(*coord, button='right')
                sleep_random(0.4, 0.2) if self.randomize else time.sleep(0.4)
        
        self.logger.info("已到达红门附近")
    
    def use_red_portal(self):
        """点击进入红门"""
        self.logger.info("进入红门...")
        in_game = self.config['coordinates']['in_game']
        
        # 多次尝试点击红门（防止点击失败）
        max_attempts = 3
        for attempt in range(max_attempts):
            coord = random_offset(in_game['red_portal_position'], 5) if self.randomize else in_game['red_portal_position']
            self.input_controller.click(*coord)
            
            if attempt < max_attempts - 1:
                sleep_random(0.5, 0.2) if self.randomize else time.sleep(0.5)
                
                # 如果第一次失败，尝试移动一下位置
                if attempt == 0:
                    self.logger.info("调整位置重试...")
                    offset_coord = random_offset(in_game['red_portal_position'], 15) if self.randomize else in_game['red_portal_position']
                    self.input_controller.click(*offset_coord, button='right')
                    sleep_random(0.3, 0.1) if self.randomize else time.sleep(0.3)
        
        sleep_random(2.0, 0.2) if self.randomize else time.sleep(2.0)
        self.logger.info("已进入神殿")
    
    def navigate_to_pindle(self):
        """传送到Pindleskin位置，带防卡机制"""
        self.logger.info("传送至Pindleskin...")
        path = self.config['coordinates']['teleport_path']
        sorc_config = self.config.get('sorceress', {})
        tp_delay = sorc_config.get('teleport_delay', 0.15)
        
        # 法师快速传送（随机化路径微调）
        for i, point in enumerate(path):
            success = False
            attempts = 0
            max_attempts = 2  # 每个点最多尝试2次
            
            while not success and attempts < max_attempts:
                # 随机偏移传送点（模拟人类不精确点击）
                if self.randomize:
                    # 如果是重试，增加偏移量避免卡在同一位置
                    offset_range = 12 if attempts > 0 else 8
                    coord = random_offset(point, offset_range)
                else:
                    coord = point
                
                self.input_controller.click(*coord, button='right')
                
                # 随机化延迟
                if self.randomize:
                    # 第一次传送可能稍慢（人类反应）
                    base_delay = tp_delay if i > 0 else tp_delay * 1.5
                    delay = random_delay(base_delay, 0.2)
                    time.sleep(delay)
                else:
                    time.sleep(tp_delay)
                
                success = True  # 假设成功，实际可以添加位置检测
                attempts += 1
                
                if not success and attempts < max_attempts:
                    self.logger.warning(f"传送点{i+1}可能失败，重试...")
        
        sleep_random(0.3, 0.2) if self.randomize else time.sleep(0.3)
    
    def kill_pindle(self):
        self.logger.info("击杀Pindleskin...")
        in_game = self.config['coordinates']['in_game']
        sorc_config = self.config.get('sorceress', {})
        safety_config = sorc_config.get('safety', {})
        
        pindle_area = in_game['pindle_spawn_area']
        cast_delay = sorc_config.get('cast_delay', 0.25)
        
        # 冰系法师战斗策略
        # 1. 使用静态力场降低血量（F2）
        static_casts = sorc_config.get('static_field_casts', 3)
        static_key = self.config['hotkeys'].get('static_field', 'f2')
        
        self.logger.info("释放静态力场...")
        for _ in range(static_casts):
            self.input_controller.press_key_by_name(static_key)
            time.sleep(0.1)
            self.input_controller.click(*pindle_area)
            time.sleep(cast_delay)
        
        # 2. 使用暴风雪击杀（F1）
        blizzard_key = self.config['hotkeys'].get('blizzard', 'f1')
        blizzard_casts = sorc_config.get('blizzard_casts', 3)
        blizzard_delay = sorc_config.get('blizzard_delay', 0.6)
        
        self.logger.info("释放暴风雪...")
        for i in range(blizzard_casts):
            self.input_controller.press_key_by_name(blizzard_key)
            time.sleep(0.1)
            # 暴风雪在Pindle位置施放
            self.input_controller.click(*pindle_area)
            time.sleep(cast_delay)
            
            # 等待暴风雪持续伤害
            if i < blizzard_casts - 1:
                time.sleep(blizzard_delay)
        
        # 3. 安全机制：传送到安全位置（避免Pindle死亡爆炸）
        if safety_config.get('teleport_away_after_cast', True):
            self.logger.info("传送到安全位置避免爆炸...")
            safe_x = pindle_area[0] + safety_config.get('safe_distance_x', 100)
            safe_y = pindle_area[1] + safety_config.get('safe_distance_y', -80)
            
            # 右键传送离开
            self.input_controller.click(safe_x, safe_y, button='right')
            time.sleep(0.3)
        
        # 4. 等待Pindle死亡和尸爆完成
        wait_time = safety_config.get('wait_before_pickup', 1.5)
        self.logger.info(f"等待{wait_time}秒确保安全...")
        time.sleep(wait_time)
        
        # 5. 预防性喝血药
        if safety_config.get('drink_potion_after_kill', True):
            health_key = self.config['hotkeys'].get('health_potion', '1')
            self.input_controller.press_key_by_name(health_key)
            time.sleep(0.2)
    
    def pickup_items(self):
        self.logger.info("拾取物品...")
        
        # 获取拾取区域配置
        pickup_config = self.config.get('pickup', {})
        item_types = pickup_config.get('item_types', ['unique'])
        scan_area = pickup_config.get('scan_area', None)
        use_smart_pickup = pickup_config.get('use_smart_pickup', True)
        
        # 额外等待尸爆完成
        if pickup_config.get('wait_for_corpse_explosion', True):
            time.sleep(0.5)
        
        if use_smart_pickup and scan_area:
            # 智能拾取：检测屏幕颜色
            self.logger.info(f"扫描物品类型: {', '.join(item_types)}")
            
            time.sleep(0.5)  # 等待物品掉落显示
            
            try:
                items = self.item_detector.find_items_in_area(
                    tuple(scan_area), 
                    item_types
                )
                
                if items:
                    self.logger.info(f"检测到 {len(items)} 个物品")
                    picked_count = 0
                    
                    for idx, (x, y, item_type) in enumerate(items):
                        # 根据物品类型判断是否拾取
                        should_pickup = False
                        
                        if item_type == 'rune':
                            should_pickup = self.item_filter.should_pickup_rune()
                            reason = "符文"
                        elif item_type == 'unique':
                            should_pickup = self.item_filter.should_pickup_unique()
                            reason = "暗金"
                        else:
                            should_pickup = True
                            reason = item_type
                        
                        if should_pickup:
                            self.logger.info(f"拾取物品 {idx+1} [{reason}]: ({x}, {y})")
                            self.input_controller.click(x, y)
                            time.sleep(0.3)
                            picked_count += 1
                        else:
                            self.logger.debug(f"跳过物品 {idx+1} [{item_type}]: 低价值")
                    
                    self.logger.info(f"拾取完成: {picked_count}/{len(items)} 个物品")
                else:
                    self.logger.info("未检测到可拾取物品")
            except Exception as e:
                self.logger.warning(f"智能拾取失败: {e}，使用固定坐标")
                self._pickup_by_positions()
        else:
            # 传统拾取：固定坐标
            self._pickup_by_positions()
        
        time.sleep(0.5)
    
    def _pickup_by_positions(self):
        """使用固定坐标拾取物品"""
        pickup_positions = self.config['coordinates'].get('legacy_pickup_positions', [])
        for pos in pickup_positions:
            self.input_controller.click(*pos)
            time.sleep(0.2)
    
    def leave_game(self):
        self.logger.info("离开游戏...")
        self.input_controller.press_key_by_name('esc')
        time.sleep(0.5)
        self.input_controller.press_key_by_name('enter')
        time.sleep(3)
    
    def run_single_game(self):
        try:
            self.create_game()
            self.navigate_to_red_portal()  # 从城镇导航到红门
            self.use_red_portal()           # 进入红门
            self.navigate_to_pindle()       # 传送到Pindle
            self.kill_pindle()
            self.pickup_items()
            self.leave_game()
            
            self.run_count += 1
            self.logger.info(f"完成第 {self.run_count} 次刷怪")
            
            # 随机化两局之间的延迟
            base_delay = self.config['bot']['delay_between_runs']
            if self.randomize:
                delay = random_delay(base_delay, 0.3)
                self.logger.info(f"等待 {delay:.2f} 秒后开始下一局")
                time.sleep(delay)
            else:
                time.sleep(base_delay)
            
        except Exception as e:
            self.logger.error(f"运行出错: {e}", exc_info=True)
            self.leave_game()
    
    def start(self):
        if not self.initialize():
            return
        
        self.is_running = True
        max_runs = self.config['bot']['runs_count']
        
        self.logger.info(f"开始刷Pindleskin，目标次数: {max_runs}")
        
        try:
            while self.is_running and self.run_count < max_runs:
                self.run_single_game()
        except KeyboardInterrupt:
            self.logger.info("用户中断")
        finally:
            self.stop()
    
    def stop(self):
        self.is_running = False
        self.logger.info(f"机器人已停止，共完成 {self.run_count} 次刷怪")


if __name__ == '__main__':
    bot = D2BaalBot()
    bot.start()
