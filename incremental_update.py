#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
from datetime import datetime

def incremental_update():
    """增量更新脚本 - 处理游戏更新后的新数据"""
    
    print("=== 增量更新开始 ===")
    print(f"更新时间: {datetime.now()}")
    
    # 1. 检查原始数据是否有更新
    original_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
    processed_file = "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"
    
    if not os.path.exists(original_file):
        print(f"❌ 原始数据文件不存在: {original_file}")
        return False
    
    if not os.path.exists(processed_file):
        print(f"❌ 处理结果文件不存在: {processed_file}")
        print("🔧 建议运行完整处理: python complete_dialogue_processor.py")
        return False
    
    # 2. 比较文件大小和时间戳
    original_size = os.path.getsize(original_file)
    original_mtime = os.path.getmtime(original_file)
    processed_mtime = os.path.getmtime(processed_file)
    
    print(f"原始文件大小: {original_size:,} bytes")
    print(f"原始文件修改时间: {datetime.fromtimestamp(original_mtime)}")
    print(f"处理文件修改时间: {datetime.fromtimestamp(processed_mtime)}")
    
    if original_mtime <= processed_mtime:
        print("✅ 原始数据没有更新，无需处理")
        return True
    
    # 3. 备份当前结果
    backup_name = f"WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(processed_file, backup_name)
    print(f"✅ 已备份当前结果到: {backup_name}")
    
    # 4. 检查原始数据行数
    original_lines = 0
    with open(original_file, 'r', encoding='utf-8') as f:
        for _ in f:
            original_lines += 1
    
    processed_lines = 0
    with open(processed_file, 'r', encoding='utf-8') as f:
        for _ in f:
            processed_lines += 1
    
    print(f"原始数据行数: {original_lines:,}")
    print(f"当前处理行数: {processed_lines:,}")
    
    if original_lines > processed_lines:
        print(f"🔄 检测到新增 {original_lines - processed_lines:,} 条对话")
    elif original_lines < processed_lines:
        print(f"⚠️  原始数据行数减少 {processed_lines - original_lines:,} 条")
    else:
        print("✅ 行数相同，但文件已更新")
    
    # 5. 运行重新处理
    print("🔄 开始重新处理...")
    import subprocess
    
    try:
        result = subprocess.run(['python', 'complete_dialogue_processor.py'], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ 处理完成")
            
            # 6. 验证新结果
            new_lines = 0
            with open(processed_file, 'r', encoding='utf-8') as f:
                for _ in f:
                    new_lines += 1
            
            print(f"新处理行数: {new_lines:,}")
            
            if new_lines == original_lines:
                print("✅ 行数匹配，处理成功")
            else:
                print(f"⚠️  行数不匹配: 原始 {original_lines:,} vs 处理 {new_lines:,}")
            
            # 7. 快速质量检查
            print("🔍 快速质量检查...")
            quality_check()
            
            return True
            
        else:
            print(f"❌ 处理失败: {result.stderr}")
            # 恢复备份
            shutil.copy2(backup_name, processed_file)
            print("✅ 已恢复备份")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 处理超时")
        return False
    except Exception as e:
        print(f"❌ 处理错误: {e}")
        return False

def quality_check():
    """快速质量检查"""
    processed_file = "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"
    
    total_lines = 0
    unknown_count = 0
    null_quest_id = 0
    empty_quest_name = 0
    
    with open(processed_file, 'r', encoding='utf-8') as f:
        for line in f:
            total_lines += 1
            data = json.loads(line.strip())
            
            if data.get('quest_name') == 'Unknown':
                unknown_count += 1
            
            if data.get('quest_id') is None:
                null_quest_id += 1
            
            if not data.get('quest_name') or data.get('quest_name') == '':
                empty_quest_name += 1
    
    mapping_rate = (total_lines - null_quest_id) / total_lines * 100
    unknown_rate = unknown_count / total_lines * 100
    quest_name_rate = (total_lines - empty_quest_name) / total_lines * 100
    
    print(f"总记录数: {total_lines:,}")
    print(f"映射率: {mapping_rate:.1f}%")
    print(f"Quest Name覆盖率: {quest_name_rate:.1f}%")
    print(f"Unknown率: {unknown_rate:.1f}%")
    
    if mapping_rate < 80:
        print("⚠️  映射率低于80%")
    if quest_name_rate < 90:
        print("⚠️  Quest Name覆盖率低于90%")
    if unknown_rate > 5:
        print("⚠️  Unknown率超过5%")
    
    if mapping_rate >= 80 and quest_name_rate >= 90 and unknown_rate <= 5:
        print("✅ 质量检查通过")

def check_config_updates():
    """检查配置文件是否有更新"""
    print("=== 配置文件更新检查 ===")
    
    config_files = {
        "ConfigDB/PlotHandBookConfig.json": "PlotHandBook配置",
        "ConfigDB/QuestNodeData.json": "QuestNodeData配置", 
        "TextMap/zh-Hans/MultiText.json": "TextMap配置"
    }
    
    for file_path, description in config_files.items():
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            size = os.path.getsize(file_path)
            print(f"{description}: {size:,} bytes, 修改时间: {datetime.fromtimestamp(mtime)}")
        else:
            print(f"❌ {description}: 文件不存在")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            check_config_updates()
        elif sys.argv[1] == "quality":
            quality_check()
        else:
            print("用法: python incremental_update.py [check|quality]")
    else:
        incremental_update()
