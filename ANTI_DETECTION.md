# 🎭 防检测功能说明

## 🤖 vs 👤 机器人 vs 人类

为了降低被检测风险，程序实现了多种随机化功能，让操作更像真人。

## ✅ 已实现的随机化功能

### 1️⃣ 游戏名称自动轮换 🎮
**原理**：重复使用相同游戏名称容易被标记

**实现模式**：

**顺序轮换**（推荐）：
```json
{
  "game_name_rotation": {
    "enabled": true,
    "mode": "sequential",
    "names": ["pindle1", "pindle2", "pindle3", "pindle4", "pindle5"],
    "change_every": 10  // 每10局更换一次
  }
}

执行效果：
第1-10局:  pindle1
第11-20局: pindle2
第21-30局: pindle3
第31-40局: pindle4
第41-50局: pindle5
第51-60局: pindle1（循环）
```

**随机轮换**：
```json
{
  "mode": "random",  // 随机选择
  "change_every": 5   // 每5局随机换一个
}

执行效果：
第1-5局:  pindle3（随机）
第6-10局: pindle1（随机）
第11-15局: pindle5（随机）
```

**随机后缀**：
```json
{
  "add_random_suffix": true  // 添加3位数字后缀
}

执行效果：
pindle1234
pindle3789
pindle2156
```

### 2️⃣ 时间延迟随机化
**原理**：人类操作不会每次都精确到毫秒级

**实现**：
```python
# 机器人模式（固定延迟）
time.sleep(1.0)  # 每次都是1秒

# 人类模拟（随机延迟）
sleep_random(1.0, 0.2)  # 0.8-1.2秒之间随机
```

**应用位置**：
- 创建游戏按钮点击
- 输入游戏名称
- 传送延迟
- 施法延迟
- 两局之间的间隔

### 2️⃣ 鼠标点击位置随机化
**原理**：人类点击不会每次都点在完全相同的像素

**实现**：
```python
# 机器人模式（精确坐标）
click(960, 400)  # 每次都点在(960, 400)

# 人类模拟（随机偏移）
coord = random_offset((960, 400), 8)  # (952-968, 392-408)范围随机
click(*coord)
```

**偏移范围**：
- 界面按钮：±3像素
- 传送点击：±8像素（更大的随机性）

### 3️⃣ 传送路径微调
**原理**：人类传送不会每次都走完全相同的路径

**实现**：
```python
# 每个传送点都随机偏移8像素
for point in teleport_path:
    coord = random_offset(point, 8)  # 每次路径略有不同
    teleport_to(coord)
```

### 4️⃣ 两局间隔随机化
**原理**：人类不会严格按固定间隔刷怪

**实现**：
```python
# 配置：delay_between_runs = 1.2秒
# 实际延迟：0.84-1.56秒之间随机（±30%）
delay = random_delay(1.2, 0.3)
```

## 📊 随机化效果对比

| 操作 | 机器人模式 | 人类模拟模式 |
|------|------------|--------------|
| 点击按钮 | 精确坐标 | ±3像素随机 |
| 传送点击 | 固定路径 | ±8像素随机 |
| 延迟时间 | 固定毫秒 | ±20-30%随机 |
| 两局间隔 | 1.2秒 | 0.84-1.56秒 |

## ⚙️ 配置选项

### 启用/禁用随机化
```json
{
  "bot": {
    "randomize_delays": true,        // true=启用 false=禁用
    "randomize_variance": 0.2,       // 时间变化范围（20%）
    "coordinate_offset": 8           // 坐标偏移范围（8像素）
  }
}
```

### 调整随机化强度

**低强度**（更快，略有风险）：
```json
{
  "randomize_delays": true,
  "randomize_variance": 0.1,    // ±10%
  "coordinate_offset": 3        // ±3像素
}
```

**中等强度**（推荐，平衡）：
```json
{
  "randomize_delays": true,
  "randomize_variance": 0.2,    // ±20%
  "coordinate_offset": 8        // ±8像素
}
```

**高强度**（最安全，稍慢）：
```json
{
  "randomize_delays": true,
  "randomize_variance": 0.3,    // ±30%
  "coordinate_offset": 12       // ±12像素
}
```

## 🎯 实际效果

### 传统机器人模式
```
[14:00:00] 创建游戏... 用时: 1.000秒
[14:00:01] 传送到 (960, 450)
[14:00:02] 传送到 (960, 380)
[14:00:03] 传送到 (960, 350)
[14:00:15] 完成第1次，等待1.200秒
[14:00:16] 完成第2次，等待1.200秒
```
❌ **明显特征**：时间和坐标完全一致

### 人类模拟模式
```
[14:00:00] 创建游戏... 用时: 1.143秒
[14:00:01] 传送到 (963, 448)
[14:00:02] 传送到 (957, 383)
[14:00:03] 传送到 (965, 347)
[14:00:15] 完成第1次，等待1.376秒
[14:00:17] 完成第2次，等待0.982秒
```
✅ **人类特征**：每次操作都略有不同

## 🛡️ 额外建议

### 1. 分批运行
```python
# 不要一次运行500次
runs_count: 50  # 每次50局

# 运行完后休息10-15分钟
```

### 2. 游戏名称自动轮换（已实现✅）
```json
{
  "game_name_rotation": {
    "enabled": true,              // 启用自动轮换
    "mode": "sequential",         // 顺序模式
    "names": [                    // 名称列表
      "pindle1", "pindle2", "pindle3", 
      "pindle4", "pindle5"
    ],
    "change_every": 10,           // 每10局更换
    "add_random_suffix": false    // 不添加随机后缀
  }
}

// 程序会自动轮换，无需手动更改！
```

**高级用法 - 随机后缀**：
```json
{
  "add_random_suffix": true  // 每次名称后加随机数字
}

// 实际游戏名：
pindle1-847
pindle2-392
pindle3-615
```

### 3. 不定期暂停
```python
# 每10-15次暂停一次
# 程序会自动记录次数
# 你可以手动Ctrl+C停止，稍后继续
```

### 4. 避免24/7运行
```
推荐模式：
- 上午刷50次，休息
- 下午刷50次，休息
- 晚上刷50次

避免模式：
- 连续8小时不间断
```

## 📈 效率影响

| 模式 | 单局时间 | 每小时次数 | 检测风险 |
|------|----------|------------|----------|
| 无随机化 | 14秒 | 257次 | ⚠️⚠️⚠️ 高 |
| 低强度 | 14.5秒 | 248次 | ⚠️⚠️ 中高 |
| **中等强度** | **15秒** | **240次** | **⚠️ 中** |
| 高强度 | 16秒 | 225次 | ✅ 低 |

**推荐**：使用中等强度（默认配置）

## ⚙️ 代码实现

### 核心随机化函数
```python
# utils.py
def random_delay(base_delay, variance=0.2):
    """生成随机延迟"""
    min_delay = base_delay * (1 - variance)
    max_delay = base_delay * (1 + variance)
    return random.uniform(min_delay, max_delay)

def random_offset(coord, max_offset=5):
    """随机偏移坐标"""
    x, y = coord
    offset_x = random.randint(-max_offset, max_offset)
    offset_y = random.randint(-max_offset, max_offset)
    return (x + offset_x, y + offset_y)
```

### 使用示例
```python
# 在game_bot.py中
if self.randomize:
    # 随机化点击
    coord = random_offset(button_position, 3)
    click(*coord)
    
    # 随机化延迟
    sleep_random(1.0, 0.2)  # 0.8-1.2秒
else:
    # 传统模式
    click(*button_position)
    time.sleep(1.0)
```

## 🎯 总结

✅ **已启用**：所有随机化功能默认开启
✅ **推荐设置**：中等强度（variance=0.2, offset=8）
✅ **预期效果**：操作更像人类，降低检测风险
⚠️ **记住**：没有100%安全，仍需谨慎使用

---

**最佳实践**：
1. 启用随机化功能 ✅
2. 分批运行（每次50局）✅
3. 定期休息（10-15分钟）✅
4. 改变游戏名称 ✅
5. 避免长时间连续运行 ✅

**现在你的程序已经像人类一样操作了！** 🎭✨
