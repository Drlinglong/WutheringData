#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import subprocess
from datetime import datetime

def emergency_diagnosis():
    """紧急诊断脚本 - 快速检查数据状态"""
    
    print("=== 紧急诊断开始 ===")
    print(f"诊断时间: {datetime.now()}")
    
    # 1. 检查关键文件是否存在
    critical_files = [
        "WutheringDialog/data/dialogs_zh-Hans.split.jsonl",
        "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl",
        "ConfigDB/PlotHandBookConfig.json",
        "ConfigDB/QuestNodeData.json",
        "TextMap/zh-Hans/MultiText.json"
    ]
    
    print("\n=== 文件完整性检查 ===")
    for file_path in critical_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} - {size:,} bytes")
        else:
            print(f"❌ {file_path} - 文件不存在!")
    
    # 2. 检查原始数据格式
    print("\n=== 原始数据格式检查 ===")
    try:
        with open("WutheringDialog/data/dialogs_zh-Hans.split.jsonl", 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            data = json.loads(first_line)
            print(f"✅ 原始数据格式正确")
            print(f"   字段: {list(data.keys())}")
    except Exception as e:
        print(f"❌ 原始数据格式错误: {e}")
    
    # 3. 检查处理结果格式
    print("\n=== 处理结果格式检查 ===")
    try:
        with open("WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl", 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            data = json.loads(first_line)
            print(f"✅ 处理结果格式正确")
            print(f"   字段: {list(data.keys())}")
    except Exception as e:
        print(f"❌ 处理结果格式错误: {e}")
    
    # 4. 快速质量检查
    print("\n=== 快速质量检查 ===")
    try:
        total_lines = 0
        unknown_count = 0
        null_quest_id = 0
        
        with open("WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl", 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                data = json.loads(line.strip())
                
                if data.get('quest_name') == 'Unknown':
                    unknown_count += 1
                
                if data.get('quest_id') is None:
                    null_quest_id += 1
        
        mapping_rate = (total_lines - null_quest_id) / total_lines * 100
        unknown_rate = unknown_count / total_lines * 100
        
        print(f"总记录数: {total_lines:,}")
        print(f"映射率: {mapping_rate:.1f}%")
        print(f"Unknown率: {unknown_rate:.1f}%")
        
        if mapping_rate < 80:
            print("⚠️  映射率低于80%，需要检查分类系统")
        
        if unknown_rate > 5:
            print("⚠️  Unknown率超过5%，需要更新分类")
            
    except Exception as e:
        print(f"❌ 质量检查失败: {e}")
    
    # 5. 检查配置文件大小
    print("\n=== 配置文件大小检查 ===")
    config_files = {
        "PlotHandBookConfig.json": (50, 100),
        "QuestNodeData.json": (14000, 15000),
        "MultiText.json": (190000, 200000)
    }
    
    for file_name, (min_lines, max_lines) in config_files.items():
        file_path = f"ConfigDB/{file_name}"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f)
            
            if min_lines <= lines <= max_lines:
                print(f"✅ {file_name}: {lines:,} 行 (正常)")
            else:
                print(f"⚠️  {file_name}: {lines:,} 行 (异常，预期 {min_lines:,}-{max_lines:,})")
        else:
            print(f"❌ {file_name}: 文件不存在")
    
    # 6. 提供修复建议
    print("\n=== 修复建议 ===")
    
    if not os.path.exists("WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"):
        print("🔧 缺少处理结果文件，运行: python complete_dialogue_processor.py")
    
    if mapping_rate < 80:
        print("🔧 映射率低，运行: python auto_scan_categories.py")
        print("🔧 然后更新 complete_dialogue_processor.py 中的分类")
    
    if unknown_rate > 5:
        print("🔧 Unknown率高，检查分类系统")
        print("🔧 运行: python auto_scan_categories.py")
    
    print("\n=== 诊断完成 ===")

def quick_fix():
    """快速修复脚本"""
    print("=== 快速修复开始 ===")
    
    # 1. 备份当前结果
    if os.path.exists("WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"):
        backup_name = f"WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename("WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl", backup_name)
        print(f"✅ 已备份到: {backup_name}")
    
    # 2. 运行处理
    print("🔄 开始重新处理...")
    try:
        result = subprocess.run(['python', 'complete_dialogue_processor.py'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ 处理完成")
        else:
            print(f"❌ 处理失败: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("❌ 处理超时")
    except Exception as e:
        print(f"❌ 处理错误: {e}")
    
    # 3. 验证结果
    print("🔍 验证结果...")
    emergency_diagnosis()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "fix":
        quick_fix()
    else:
        emergency_diagnosis()
