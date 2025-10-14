# 🎮 游戏名称自动轮换功能

## 💡 为什么需要轮换游戏名称？

**问题**：重复使用相同的游戏名称容易被标记为机器人
- 游戏服务器可以追踪特定游戏名的创建频率
- 同一名称短时间内大量创建 → 异常行为

**解决方案**：自动轮换多个不同的游戏名称

## ⚙️ 配置选项

### 基础配置
```json
{
  "bot": {
    "game_name_rotation": {
      "enabled": true,                    // 是否启用轮换
      "mode": "sequential",               // 轮换模式
      "names": [                          // 游戏名称列表
        "pindle1",
        "pindle2", 
        "pindle3",
        "pindle4",
        "pindle5"
      ],
      "change_every": 10,                 // 每N局更换一次
      "add_random_suffix": false          // 是否添加随机后缀
    }
  }
}
```

## 📊 轮换模式详解

### 模式1: 顺序轮换（sequential）
**特点**：按固定顺序依次使用

```json
{
  "mode": "sequential",
  "names": ["pindle1", "pindle2", "pindle3"],
  "change_every": 10
}
```

**效果**：
```
第1-10局:   pindle1
第11-20局:  pindle2
第21-30局:  pindle3
第31-40局:  pindle1  ← 循环回第一个
第41-50局:  pindle2
```

**优点**：
- ✅ 可预测
- ✅ 容易监控
- ✅ 适合固定刷怪模式

**推荐场景**：日常使用，分批刷怪

---

### 模式2: 随机轮换（random）
**特点**：随机选择游戏名称

```json
{
  "mode": "random",
  "names": ["pindle1", "pindle2", "pindle3", "pindle4", "pindle5"],
  "change_every": 5
}
```

**效果**：
```
第1-5局:   pindle3  ← 随机
第6-10局:  pindle1  ← 随机
第11-15局: pindle5  ← 随机
第16-20局: pindle2  ← 随机
```

**优点**：
- ✅ 更自然
- ✅ 难以预测
- ✅ 更像真实玩家

**推荐场景**：长时间运行，高度随机化

---

### 模式3: 随机后缀（add_random_suffix）
**特点**：在基础名称后添加随机数字

```json
{
  "mode": "sequential",
  "names": ["pindle"],
  "change_every": 1,
  "add_random_suffix": true
}
```

**效果**：
```
第1局:  pindle847
第2局:  pindle392
第3局:  pindle615
第4局:  pindle128
```

**优点**：
- ✅ 每局都不同
- ✅ 最高随机性
- ✅ 难以追踪

**缺点**：
- ⚠️ 可能无法加入自己的游戏（如果需要多角色）

**推荐场景**：极度谨慎，追求最高安全性

---

## 🎯 推荐配置方案

### 方案A: 保守型（新手推荐）
```json
{
  "enabled": true,
  "mode": "sequential",
  "names": ["pindle1", "pindle2", "pindle3"],
  "change_every": 20,              // 每20局换一次
  "add_random_suffix": false
}
```
**特点**：稳定可靠，容易监控

---

### 方案B: 平衡型（默认推荐）
```json
{
  "enabled": true,
  "mode": "sequential",
  "names": ["pindle1", "pindle2", "pindle3", "pindle4", "pindle5"],
  "change_every": 10,              // 每10局换一次
  "add_random_suffix": false
}
```
**特点**：平衡安全和效率

---

### 方案C: 激进型（高安全需求）
```json
{
  "enabled": true,
  "mode": "random",
  "names": ["run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8"],
  "change_every": 5,               // 每5局换一次
  "add_random_suffix": false
}
```
**特点**：高度随机，难以追踪

---

### 方案D: 极限型（最高安全性）
```json
{
  "enabled": true,
  "mode": "random",
  "names": ["p", "pd", "pind", "pindle", "run"],
  "change_every": 3,               // 每3局换一次
  "add_random_suffix": true        // 添加随机后缀
}
```
**特点**：每局都不同，最高安全性

---

## 📈 实际运行示例

### 示例1: 方案B运行50局
```log
[INFO] 创建游戏: pindle1... (第1局)
[INFO] 创建游戏: pindle1... (第5局)
[INFO] 创建游戏: pindle1... (第10局)
[INFO] 创建游戏: pindle2... (第11局) ← 自动切换
[INFO] 创建游戏: pindle2... (第15局)
[INFO] 创建游戏: pindle2... (第20局)
[INFO] 创建游戏: pindle3... (第21局) ← 自动切换
[INFO] 创建游戏: pindle3... (第30局)
[INFO] 创建游戏: pindle4... (第31局) ← 自动切换
```

### 示例2: 方案C随机模式
```log
[INFO] 创建游戏: run5... (第1局)   ← 随机
[INFO] 创建游戏: run5... (第5局)
[INFO] 创建游戏: run2... (第6局)   ← 随机切换
[INFO] 创建游戏: run2... (第10局)
[INFO] 创建游戏: run7... (第11局)  ← 随机切换
[INFO] 创建游戏: run7... (第15局)
[INFO] 创建游戏: run1... (第16局)  ← 随机切换
```

### 示例3: 方案D随机后缀
```log
[INFO] 创建游戏: p847... (第1局)
[INFO] 创建游戏: pindle392... (第2局)
[INFO] 创建游戏: run615... (第3局)
[INFO] 创建游戏: pd128... (第4局)
[INFO] 创建游戏: pind956... (第5局)
```

---

## 🔧 高级技巧

### 技巧1: 时间段区分
**思路**：不同时间段使用不同名称组

**上午刷怪**：
```json
{
  "names": ["morning1", "morning2", "morning3"]
}
```

**下午刷怪**：
```json
{
  "names": ["afternoon1", "afternoon2", "afternoon3"]
}
```

**晚上刷怪**：
```json
{
  "names": ["evening1", "evening2", "evening3"]
}
```

### 技巧2: 主题变化
使用不同主题的名称组：
```json
{
  "names": [
    "p1", "p2", "p3",           // 短名称组
    "pindle1", "pindle2",       // 标准组
    "baalrun1", "baalrun2",     // 伪装组
    "mf01", "mf02", "mf03"      // MF组
  ],
  "change_every": 8
}
```

### 技巧3: 多账号协同
**账号1**：
```json
{"names": ["p1", "p3", "p5", "p7", "p9"]}
```

**账号2**：
```json
{"names": ["p2", "p4", "p6", "p8", "p10"]}
```

避免名称冲突

---

## 🛠️ 故障排除

### 问题1: 名称没有更换
**检查**：
```json
{
  "enabled": true,  // ← 确保为true
  "change_every": 10  // ← 确认已运行足够局数
}
```

### 问题2: 无法加入游戏
**原因**：可能名称已被占用

**解决**：
```json
{
  "add_random_suffix": true  // 添加随机后缀避免重复
}
```

### 问题3: 想手动指定名称
**方法**：临时禁用轮换
```json
{
  "enabled": false,  // 禁用轮换
  "game_name": "my_custom_name"  // 使用固定名称
}
```

---

## 📊 效果评估

| 配置 | 安全性 | 便利性 | 效率 |
|------|--------|--------|------|
| 禁用轮换 | ⚠️ 低 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 方案A | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 方案B | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 方案C | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 方案D | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## ✅ 最佳实践总结

1. **日常使用**：方案B（5个名称，每10局换）✅
2. **谨慎使用**：方案C（随机模式）✅
3. **极度谨慎**：方案D（随机+后缀）✅
4. **配合休息**：每50局休息10-15分钟✅
5. **定期更换**：每周更新名称列表✅

**现在游戏名称会自动轮换，无需手动操作！** 🎮✨
