#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
from datetime import datetime

def one_click_fix():
    """一键修复脚本 - 自动处理所有问题"""
    
    print("=== 一键修复开始 ===")
    print(f"修复时间: {datetime.now()}")
    
    # 1. 检查环境
    print("\n=== 环境检查 ===")
    required_files = [
        "ConfigDB/PlotHandBookConfig.json",
        "ConfigDB/QuestNodeData.json",
        "TextMap/zh-Hans/MultiText.json"
    ]
    
    # 检查原始数据文件
    original_files = [
        "WutheringDialog/data/dialogs_zh-Hans.jsonl",
        "WutheringDialog/data/dialogs_zh-Hans.cleaned.jsonl",
        "WutheringDialog/data/dialogs_zh-Hans.enriched.jsonl"
    ]
    
    split_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"❌ 缺少文件: {file_path}")
        else:
            print(f"✅ 文件存在: {file_path}")
    
    # 检查原始数据文件
    original_file = None
    for file_path in original_files:
        if os.path.exists(file_path):
            original_file = file_path
            print(f"✅ 找到原始数据: {file_path}")
            break
    
    if not original_file:
        print(f"❌ 没有找到原始数据文件")
        print("请确保以下文件之一存在:")
        for file_path in original_files:
            print(f"  - {file_path}")
        return False
    
    # 检查split文件
    if not os.path.exists(split_file):
        print(f"⚠️  缺少split文件: {split_file}")
        print("🔄 将自动生成split数据...")
    else:
        print(f"✅ split文件存在: {split_file}")
    
    if missing_files:
        print(f"\n❌ 缺少关键文件，无法继续修复")
        print("请确保以下文件存在:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    # 2. 备份现有结果
    print("\n=== 备份现有结果 ===")
    processed_file = "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"
    
    if os.path.exists(processed_file):
        backup_name = f"WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(processed_file, backup_name)
        print(f"✅ 已备份到: {backup_name}")
    else:
        print("ℹ️  没有现有结果需要备份")
    
    # 3. 生成split数据（如果需要）
    if not os.path.exists(split_file):
        print("\n=== 生成Split数据 ===")
        try:
            result = subprocess.run(['python', 'generate_split_data.py'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Split数据生成完成")
            else:
                print(f"❌ Split数据生成失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Split数据生成超时")
            return False
        except Exception as e:
            print(f"❌ Split数据生成错误: {e}")
            return False
    
    # 4. 运行扫描脚本
    print("\n=== 扫描数据模式 ===")
    try:
        result = subprocess.run(['python', 'auto_scan_categories.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ 扫描完成")
        else:
            print(f"⚠️  扫描警告: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  扫描超时，继续处理")
    except Exception as e:
        print(f"⚠️  扫描错误: {e}")
    
    # 5. 运行完整处理
    print("\n=== 开始数据处理 ===")
    try:
        result = subprocess.run(['python', 'complete_dialogue_processor.py'], 
                              capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ 数据处理完成")
        else:
            print(f"❌ 数据处理失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 数据处理超时")
        return False
    except Exception as e:
        print(f"❌ 数据处理错误: {e}")
        return False
    
    # 6. 质量检查
    print("\n=== 质量检查 ===")
    try:
        result = subprocess.run(['python', 'analyze_final_quality.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 质量检查完成")
            # 解析关键指标
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if '成功映射:' in line:
                    mapping_rate = float(line.split('(')[1].split('%')[0])
                    if mapping_rate >= 80:
                        print(f"✅ 映射率: {mapping_rate:.1f}% (良好)")
                    else:
                        print(f"⚠️  映射率: {mapping_rate:.1f}% (需要改进)")
                elif 'Quest Name 填充:' in line:
                    quest_name_rate = float(line.split('(')[1].split('%')[0])
                    if quest_name_rate >= 90:
                        print(f"✅ Quest Name覆盖率: {quest_name_rate:.1f}% (良好)")
                    else:
                        print(f"⚠️  Quest Name覆盖率: {quest_name_rate:.1f}% (需要改进)")
        else:
            print(f"⚠️  质量检查失败: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⚠️  质量检查超时")
    except Exception as e:
        print(f"⚠️  质量检查错误: {e}")
    
    # 7. 生成报告
    print("\n=== 生成修复报告 ===")
    report_file = f"fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"一键修复报告\n")
        f.write(f"修复时间: {datetime.now()}\n")
        f.write(f"修复状态: {'成功' if True else '失败'}\n")
        f.write(f"\n处理文件:\n")
        f.write(f"- 原始数据: {original_file}\n")
        f.write(f"- Split数据: WutheringDialog/data/dialogs_zh-Hans.split.jsonl\n")
        f.write(f"- 处理结果: WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl\n")
        f.write(f"- 备份文件: {backup_name if 'backup_name' in locals() else '无'}\n")
    
    print(f"✅ 修复报告已保存到: {report_file}")
    
    # 8. 最终状态
    print("\n=== 修复完成 ===")
    print("✅ 一键修复已完成")
    print("📁 处理结果: WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl")
    print("📊 质量报告: analyze_final_quality.py")
    print("📋 修复报告:", report_file)
    
    return True

def quick_scan():
    """快速扫描 - 只检查不处理"""
    print("=== 快速扫描 ===")
    
    # 检查文件状态
    files_to_check = [
        "WutheringDialog/data/dialogs_zh-Hans.split.jsonl",
        "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl",
        "ConfigDB/PlotHandBookConfig.json",
        "ConfigDB/QuestNodeData.json",
        "TextMap/zh-Hans/MultiText.json"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"✅ {file_path}")
            print(f"   大小: {size:,} bytes")
            print(f"   修改: {mtime}")
        else:
            print(f"❌ {file_path} - 不存在")
    
    # 快速质量检查
    processed_file = "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"
    if os.path.exists(processed_file):
        print("\n=== 快速质量检查 ===")
        try:
            total_lines = 0
            unknown_count = 0
            null_quest_id = 0
            
            with open(processed_file, 'r', encoding='utf-8') as f:
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
            
            if mapping_rate >= 80 and unknown_rate <= 5:
                print("✅ 数据质量良好")
            else:
                print("⚠️  数据质量需要改进")
                
        except Exception as e:
            print(f"❌ 质量检查失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            quick_scan()
        elif sys.argv[1] == "fix":
            one_click_fix()
        else:
            print("用法:")
            print("  python one_click_fix.py        # 一键修复")
            print("  python one_click_fix.py scan   # 快速扫描")
            print("  python one_click_fix.py fix    # 强制修复")
    else:
        one_click_fix()
