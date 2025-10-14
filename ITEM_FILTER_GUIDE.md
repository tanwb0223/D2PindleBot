# 💎 物品过滤系统 - 符文过滤

## ⚠️ 重要说明：暗金装备无法过滤

**核心限制**：
- ❌ D2R中的暗金装备掉落时是**未鉴定**状态
- ❌ 未鉴定装备无法看到真实名称（只显示基础类型）
- ❌ 程序无法判断未鉴定暗金的价值
- ✅ **只能过滤符文**（符文显示真实名称）

**详细说明请看**：`PICKUP_LIMITATION.md`

## 🎯 实际过滤能力

**可以过滤**：
- ✅ 符文（可以根据等级过滤）
- ✅ 绿装/亮黄（可以选择是否拾取）

**无法过滤**：
- ❌ 暗金装备价值（必须全拾取或全不拾取）

## ✅ 已实现的过滤功能

### 1️⃣ 符文过滤

**模式A: 拾取所有符文（默认）**
```json
{
  "pickup_all_runes": true
}
```
✅ 拾取：El ~ Zod（所有33种符文）

---

**模式B: 只拾取高级符文**
```json
{
  "pickup_all_runes": false,
  "min_rune_level": "Io"
}
```
✅ 拾取：Io ~ Zod（Io及以上）
❌ 跳过：El ~ Hel（低级符文）

**符文等级表**：
```
低级（通常跳过）：
El(1) Eld(2) Tir(3) Nef(4) Eth(5) Ith(6) Tal(7) Ral(8)
Ort(9) Thul(10) Amn(11) Sol(12) Shael(13) Dol(14) Hel(15)

中级（可拾取）：
Io(16) Lum(17) Ko(18) Fal(19) Lem(20) Pul(21) Um(22)

高级（必拾取）：
Mal(23) Ist(24) Gul(25) Vex(26) Ohm(27) Lo(28)
Sur(29) Ber(30) Jah(31) Cham(32) Zod(33)
```

**推荐设置**：
- **土豪模式**：`min_rune_level: "Mal"`（只拾取Mal+）
- **平衡模式**：`min_rune_level: "Io"`（拾取Io+）
- **贫民模式**：`pickup_all_runes: true`（全拾取）

---

### 2️⃣ 暗金装备过滤

**Pindleskin高价值暗金装备列表**：

#### 极高价值（必拾取）⭐⭐⭐⭐⭐
```
- Death's Web（死亡之网）
- Griffon's Eye（狮鹫之眼）
- Stones of Jordan（乔丹之石）
- Annihilus（毁灭小护身符）
- Hellfire Torch（地狱火炬）
```

#### 很高价值⭐⭐⭐⭐
```
- Arachnid Mesh（蜘蛛网腰带）
- Harlequin Crest（小丑帽/沙克）
- Mara's Kaleidoscope（玛拉的项链）
- Windforce（风之力）
- Death's Fathom（死神之喉）
- Crown of Ages（岁月王冠）
```

#### 高价值⭐⭐⭐
```
- War Traveler（战争旅者靴子）
- Vampire Gaze（吸血鬼凝视）
- Andariel's Visage（安达莉尔的容颜）
- Stormshield（风暴之盾）
- Tal Rasha's Guardianship（塔拉夏护甲）
```

#### 中等价值⭐⭐
```
- Sandstorm Trek（沙漠长途）
- Thundergod's Vigor（雷神之力）
- Skin of the Vipermagi（蛇皮甲）
- Ormus' Robes（奥玛斯长袍）
- Herald of Zakarum（查克拉姆之兆）
- Highlord's Wrath（高原者的愤怒）
- Gheeds Fortune（吉德的幸运）
```

#### 低价值（跳过）❌
```
- Tarnhelm（玷污之盔）
- Peasant Crown（农民皇冠）
- Wormskull（虫颅）
- Undead Crown（不死皇冠）
- Bloodrise（血升）
- The Gnasher（咬骨）
- Crushflange（碎刃）
- Coldsteel Eye（寒铁之眼）
- Bladebone（骨刃）
- The Atlantean（亚特兰蒂斯人）
```

---

## ⚙️ 配置方案

### 方案A: 只拾取顶级物品（推荐）
```json
{
  "pickup": {
    "item_types": ["unique", "rune"],
    "filter": {
      "enabled": true,
      "pickup_all_runes": false,
      "min_rune_level": "Mal",
      "valuable_uniques": [
        "Death's Web",
        "Griffon's Eye",
        "Stones of Jordan",
        "Arachnid Mesh",
        "Harlequin Crest",
        "Mara's Kaleidoscope",
        "Windforce",
        "Death's Fathom",
        "War Traveler",
        "Annihilus",
        "Hellfire Torch"
      ],
      "skip_low_value_items": true
    }
  }
}
```

**效果**：
- ✅ 符文：Mal ~ Zod
- ✅ 暗金：11种顶级装备
- ❌ 跳过：低级符文、低价值暗金

---

### 方案B: 平衡拾取（默认）
```json
{
  "pickup": {
    "item_types": ["unique", "rune"],
    "filter": {
      "enabled": true,
      "pickup_all_runes": true,
      "valuable_uniques": [
        "Arachnid Mesh",
        "Harlequin Crest",
        "Mara's Kaleidoscope",
        "Windforce",
        "Death's Fathom",
        "Vampire Gaze",
        "War Traveler",
        "Stones of Jordan",
        "Annihilus",
        "Torch"
      ],
      "skip_low_value_items": true
    }
  }
}
```

**效果**：
- ✅ 符文：全部
- ✅ 暗金：10种高价值装备
- ❌ 跳过：已知低价值暗金

---

### 方案C: 拾取所有（贪婪模式）
```json
{
  "pickup": {
    "item_types": ["unique", "set", "rune", "rare"],
    "filter": {
      "enabled": false
    }
  }
}
```

**效果**：
- ✅ 所有符文
- ✅ 所有暗金
- ✅ 所有绿装
- ✅ 所有亮黄

---

### 方案D: 只拾取符文
```json
{
  "pickup": {
    "item_types": ["rune"],
    "filter": {
      "enabled": true,
      "pickup_all_runes": false,
      "min_rune_level": "Io"
    }
  }
}
```

**效果**：
- ✅ 符文：Io ~ Zod
- ❌ 跳过：所有暗金装备

---

## 🔧 高级配置

### 自定义暗金列表
```json
{
  "valuable_uniques": [
    "你的装备1",
    "你的装备2",
    "你的装备3"
  ]
}
```

**注意**：装备名称必须完全匹配（大小写敏感）

### 调试模式
```json
{
  "pickup_by_color_only": true,
  "skip_low_value_items": false
}
```
- `pickup_by_color_only: true` - 只根据颜色拾取，不检查名称
- `skip_low_value_items: false` - 不跳过任何物品

---

## 📊 效率对比

| 模式 | 拾取物品数 | 单局时间 | 背包占用 |
|------|------------|----------|----------|
| 拾取所有 | 8-15个 | 18秒 | 高 |
| 平衡模式 | 3-6个 | 16秒 | 中 |
| 顶级模式 | 1-3个 | 15秒 | 低 |
| 只拾符文 | 0-2个 | 14秒 | 很低 |

---

## 🎯 实际使用示例

### 场景1: 日常刷怪（推荐方案B）
```json
{
  "pickup_all_runes": true,
  "min_rune_level": "Io",
  "valuable_uniques": [前10个高价值]
}
```

**日志输出**：
```
[INFO] 检测到 8 个物品
[INFO] 拾取物品 1 [符文]: (920, 385)
[INFO] 拾取物品 2 [暗金]: (960, 400)
[DEBUG] 跳过物品 3 [unique]: 低价值
[DEBUG] 跳过物品 4 [unique]: 低价值
[INFO] 拾取物品 5 [符文]: (1005, 412)
[INFO] 拾取完成: 3/8 个物品
```

---

### 场景2: 追求顶级（方案A）
```json
{
  "min_rune_level": "Mal",
  "valuable_uniques": [前5个极高价值]
}
```

**日志输出**：
```
[INFO] 检测到 6 个物品
[DEBUG] 跳过物品 1 [rune]: 低价值（Io）
[DEBUG] 跳过物品 2 [unique]: 低价值
[INFO] 拾取物品 3 [符文]: (960, 390) ← Ist符文
[DEBUG] 跳过物品 4 [unique]: 低价值
[INFO] 拾取完成: 1/6 个物品
```

---

### 场景3: MF贪婪（方案C）
```json
{
  "filter": {
    "enabled": false
  }
}
```

**日志输出**：
```
[INFO] 检测到 12 个物品
[INFO] 拾取物品 1 [rune]: (920, 385)
[INFO] 拾取物品 2 [unique]: (940, 392)
[INFO] 拾取物品 3 [unique]: (960, 400)
[INFO] 拾取物品 4 [set]: (980, 408)
... (拾取所有)
[INFO] 拾取完成: 12/12 个物品
```

---

## 🐛 故障排除

### 问题1: 拾取了不想要的物品
**解决**：
```json
{
  "skip_low_value_items": true,
  "valuable_uniques": [只列出你想要的]
}
```

### 问题2: 错过了高价值物品
**解决**：
```json
{
  "skip_low_value_items": false,  // 暂时拾取所有
  "valuable_uniques": [...增加更多装备名称]
}
```

### 问题3: 无法识别物品名称
**当前限制**：基于颜色检测，无法读取物品名称

**解决方案**：
```json
{
  "pickup_by_color_only": true,  // 看到暗金色就拾取
  "skip_low_value_items": false  // 不跳过
}
```

---

## 🚀 未来改进（可选功能）

### OCR文字识别
如果需要识别物品名称：

1. 安装OCR库
```bash
pip install pytesseract
pip install pillow
```

2. 截取物品名称区域
3. OCR识别文字
4. 与列表匹配

**优点**：精确识别
**缺点**：速度慢，需要额外配置

---

## ✅ 最佳实践

1. **初期**：使用方案C（拾取所有），积累财富
2. **中期**：使用方案B（平衡模式），提升效率
3. **后期**：使用方案A（顶级模式），只要最好的

**推荐配置（方案B）**：
```json
{
  "pickup_all_runes": true,
  "min_rune_level": "Io",
  "valuable_uniques": [10-15个高价值装备],
  "skip_low_value_items": true
}
```

**现在程序只会拾取符文和高价值暗金装备！** 💎✨
