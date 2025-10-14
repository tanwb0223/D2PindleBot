# 暗黑破坏神2 自动刷Pindleskin程序

## 功能特性

- 自动创建游戏
- 自动点击红门进入尼拉塞克神殿
- 自动传送到Pindleskin位置
- 自动击杀Pindleskin
- 自动拾取物品
- 自动离开游戏并重新开始（速度快，适合刷装备）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

编辑 `config.json` 文件：

1. **game**: 游戏窗口标题和进程名
2. **bot**: 游戏名称、密码、难度、刷怪次数等
3. **hotkeys**: 技能快捷键设置（传送、攻击技能、TP、药水等）
4. **coordinates**: 界面坐标（需要根据你的屏幕分辨率调整）
   - `red_portal_position`: 哈洛加斯红门位置
   - `pindle_path`: 传送到Pindleskin的路径点
   - `pindle_attack_position`: 攻击Pindleskin的位置
   - `pickup_positions`: 拾取物品的位置（周围4个点）

### 获取坐标的方法

运行以下Python代码查看鼠标实时坐标：

```python
import pyautogui
import time

print("5秒后开始显示坐标，移动鼠标到目标位置...")
time.sleep(5)

for i in range(10):
    x, y = pyautogui.position()
    print(f"坐标: ({x}, {y})")
    time.sleep(1)
```

## 使用方法

```bash
python main.py
```

或指定配置文件：

```bash
python main.py my_config.json
```

## 前置条件

✅ **必须满足**：
- 角色已完成第五章安亚救援任务（解锁红门）
- 角色在哈洛加斯城镇
- 难度：地狱难度（Hell）
- 推荐职业：法师（传送技能）或其他高伤害职业

## 注意事项

⚠️ **警告**：
- 使用自动化程序可能违反游戏服务条款
- 有封号风险，请谨慎使用
- 建议在单机模式或私服测试
- 首次使用建议设置少量运行次数，观察是否正常工作
- Pindleskin刷新速度快，效率高，适合刷装备和符文

## 自定义优化

根据你的角色职业和装备，需要调整：

1. 移动路径坐标
2. 攻击技能和释放频率
3. 药水使用策略
4. 延迟时间

## 故障排除

- **找不到游戏窗口**: 检查 config.json 中的 window_title 是否正确
- **坐标不准确**: 使用上述方法重新获取坐标
- **角色卡住**: 调整移动路径坐标
- **频繁死亡**: 增加药水使用频率，优化战斗策略
