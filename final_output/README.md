# WutheringData Processor

鸣潮游戏数据处理器 - 将游戏配置文件转换为高质量的RAG数据集

## 📋 项目简介

本项目提供了一套完整的数据处理工具，用于将鸣潮游戏（Wuthering Waves）的配置文件转换为适合RAG（检索增强生成）应用的高质量数据集。

## 🎯 数据来源

本项目使用的原始数据来自：[Dimbreath/WutheringData](https://github.com/Dimbreath/WutheringData)

感谢 Dimbreath 及其团队提供完整的游戏数据！

## 📦 输出文件

处理完成后，你将得到以下6个JSONL格式的数据文件：

1. **`dialogs_zh-Hans_complete.jsonl`** ⭐ 最重要
   - 完整对话数据（58,488条记录）
   - 映射率: 80.2%
   - Quest Name覆盖率: 93.3%
   - 包含完整的元数据：quest_id, quest_name, chapter_title, section_desc等

2. **`characters.jsonl`** - 角色信息数据
3. **`items.jsonl`** - 物品信息数据
4. **`weapons.jsonl`** - 武器信息数据
5. **`enemies.jsonl`** - 敌人信息数据
6. **`achievements.jsonl`** - 成就信息数据

## 🛠️ 核心特性

- ✅ 自动映射quest_id
- ✅ 智能分类对话类型（生态、角色、主线、支线）
- ✅ 补全元数据信息
- ✅ 质量验证和报告
- ✅ 支持增量更新

## 📂 项目结构

```
项目根目录/
├── output/                           # 最终输出目录（处理后生成）
│   ├── dialogs_zh-Hans_complete.jsonl    # 完整对话数据
│   ├── characters.jsonl                  # 角色信息
│   ├── items.jsonl                       # 物品信息
│   ├── weapons.jsonl                     # 武器信息
│   ├── enemies.jsonl                      # 敌人信息
│   └── achievements.jsonl                # 成就信息
│
├── ConfigDB/                          # 游戏配置文件（需从WutheringData获取）
├── TextMap/                           # 文本映射（需从WutheringData获取）
└── scripts/                           # 处理脚本
    ├── complete_dialogue_processor.py   # 主处理器
    ├── generate_split_data.py          # 生成split格式
    ├── auto_scan_categories.py         # 扫描新模式
    ├── analyze_final_quality.py       # 质量分析
    ├── extract_characters.py
    ├── extract_items.py
    ├── extract_weapons.py
    ├── extract_enemies.py
    └── extract_achievements.py
```

## 🚀 快速开始

### 前置要求

- Python 3.7+
- 从 [WutheringData](https://github.com/Dimbreath/WutheringData) 获取原始数据

### 使用方法

1. **获取原始数据**
   ```bash
   git clone https://github.com/Dimbreath/WutheringData.git
   ```

2. **准备数据目录**
   ```bash
   # 将本项目克隆到本地
   git clone <your-repo-url>
   cd wutheringdata-processor
   
   # 复制 ConfigDB/ 和 TextMap/ 目录到项目根目录
   cp -r ../WutheringData/ConfigDB .
   cp -r ../WutheringData/TextMap .
   ```

3. **运行处理脚本**
   ```bash
   # 进入scripts目录
   cd scripts
   
   # 生成split数据
   python generate_split_data.py
   
   # 处理对话数据（输出到 ../output/ 目录）
   python complete_dialogue_processor.py
   
   # 验证质量
   python analyze_final_quality.py
   ```

4. **查看结果**
   处理后的文件将保存在项目根目录的 `output/` 目录中。

5. **更新其他数据（可选）**
   ```bash
   # 仍在scripts目录下运行
   python extract_characters.py
   python extract_items.py
   python extract_weapons.py
   python extract_enemies.py
   python extract_achievements.py
   ```

## 📊 数据质量

- **映射率**: 80.2% (46,890 / 58,488)
- **Quest Name覆盖率**: 93.3%
- **Chapter Title覆盖率**: 35.3%
- **Section Desc覆盖率**: 60.1%

## 🔄 增量更新

当鸣潮游戏更新后，可以快速更新数据：

```bash
cd final_output

# 1. 替换 ConfigDB/ 和 TextMap/ 目录为新版本
# 2. 重新处理
python scripts/complete_dialogue_processor.py

# 3. 验证质量
python scripts/analyze_final_quality.py
```

详见 `增量更新指南.md`

## 🎯 应用场景

- RAG（检索增强生成）应用
- 游戏数据分析
- 对话系统训练
- 知识图谱构建

## 📝 技术特点

- **双重处理策略**: 第一阶段提取 + 第二阶段精炼
- **智能分类系统**: 自动识别551种数据模式
- **动态映射**: 处理复杂的ID系统
- **质量监控**: 实时验证数据完整性

## 🤝 致谢

- 原始数据来源: [Dimbreath/WutheringData](https://github.com/Dimbreath/WutheringData)
- 游戏: Wuthering Waves (鸣潮) by Kuro Games

## 📄 许可证

本项目遵循原始数据源的许可证要求。

## ⚠️ 重要说明

**数据质量**: 本项目处理的数据来自游戏配置文件，数据质量取决于游戏公司的数据设计。我们已尽力处理了复杂的ID映射、动态键名匹配等问题，但某些数据仍可能存在不完整的情况。建议在使用前进行质量检查。

---

**注意**: 本项目仅用于学习和研究目的。请遵守游戏开发商的相关条款。