"""
坐标获取辅助工具 - 针对1920x1080 D2R
用于快速获取游戏中各个位置的准确坐标
"""
import pyautogui
import time
import keyboard
from datetime import datetime


class CoordinateHelper:
    def __init__(self):
        self.coordinates = {}
        self.running = True
    
    def start(self):
        print("=" * 70)
        print("D2R 坐标获取工具 (1920x1080)")
        print("=" * 70)
        print("\n快捷键说明:")
        print("  空格键  - 记录当前坐标")
        print("  1-9键   - 保存坐标到对应编号")
        print("  S键     - 保存所有坐标到文件")
        print("  ESC键   - 退出程序")
        print("\n推荐获取的坐标（按顺序）:")
        print("  1. 大厅 - 创建游戏按钮")
        print("  2. 大厅 - 游戏名称输入框")
        print("  3. 大厅 - 密码输入框")
        print("  4. 大厅 - 开始游戏按钮")
        print("  5. 游戏内 - 红门位置")
        print("  6. 游戏内 - Pindle刷新区域中心")
        print("  7-9. 传送路径的三个点")
        print("=" * 70)
        print("\n移动鼠标到目标位置，按空格键记录坐标...")
        print()
        
        # 设置快捷键
        keyboard.on_press_key("space", lambda _: self.record_coordinate())
        keyboard.on_press_key("s", lambda _: self.save_coordinates())
        keyboard.on_press_key("esc", lambda _: self.stop())
        
        for i in range(1, 10):
            keyboard.on_press_key(str(i), lambda e, idx=i: self.save_to_slot(idx))
        
        # 主循环：实时显示坐标
        try:
            last_pos = None
            while self.running:
                x, y = pyautogui.position()
                if (x, y) != last_pos:
                    print(f"\r当前坐标: ({x:4d}, {y:4d})    ", end="", flush=True)
                    last_pos = (x, y)
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        
        print("\n\n程序已退出")
    
    def record_coordinate(self):
        x, y = pyautogui.position()
        timestamp = datetime.now().strftime("%H:%M:%S")
        coord_id = f"coord_{len(self.coordinates) + 1}"
        self.coordinates[coord_id] = (x, y)
        print(f"\n[{timestamp}] 已记录: {coord_id} = ({x}, {y})")
    
    def save_to_slot(self, slot_num):
        x, y = pyautogui.position()
        coord_names = [
            "创建游戏按钮",
            "游戏名称输入",
            "密码输入",
            "开始游戏按钮",
            "红门位置",
            "Pindle区域",
            "传送点1",
            "传送点2",
            "传送点3"
        ]
        
        name = coord_names[slot_num - 1] if slot_num <= len(coord_names) else f"位置{slot_num}"
        self.coordinates[f"slot_{slot_num}_{name}"] = (x, y)
        print(f"\n[{slot_num}] {name}: ({x}, {y})")
    
    def save_coordinates(self):
        if not self.coordinates:
            print("\n未记录任何坐标！")
            return
        
        filename = f"coordinates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("D2R 坐标记录 (1920x1080)\n")
            f.write("=" * 50 + "\n\n")
            
            for name, (x, y) in self.coordinates.items():
                f.write(f"{name}: [{x}, {y}]\n")
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("JSON格式（可直接复制到config.json）:\n\n")
            
            for name, (x, y) in self.coordinates.items():
                clean_name = name.replace("slot_", "").split("_", 1)[-1]
                f.write(f'  "{clean_name}": [{x}, {y}],\n')
        
        print(f"\n✓ 坐标已保存到: {filename}")
        print(f"  共记录 {len(self.coordinates)} 个坐标")
    
    def stop(self):
        self.running = False
        if self.coordinates:
            self.save_coordinates()


def main():
    helper = CoordinateHelper()
    helper.start()


if __name__ == '__main__':
    main()
