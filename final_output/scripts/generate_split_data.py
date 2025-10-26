#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, List

def generate_split_dialogue():
    """从原始对话数据生成split格式的对话文件"""
    
    print("=== 生成Split对话数据 ===")
    
    # 检查原始文件
    original_file = "WutheringDialog/data/dialogs_zh-Hans.jsonl"
    output_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
    
    if not os.path.exists(original_file):
        print(f"❌ 原始文件不存在: {original_file}")
        print("请确保以下文件存在:")
        print("  - WutheringDialog/data/dialogs_zh-Hans.jsonl")
        return False
    
    print(f"✅ 找到原始文件: {original_file}")
    
    # 读取原始数据
    print("📖 读取原始数据...")
    original_data = []
    
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num % 10000 == 0:
                    print(f"  已读取 {line_num:,} 行...")
                
                try:
                    data = json.loads(line.strip())
                    original_data.append(data)
                except json.JSONDecodeError as e:
                    print(f"⚠️  第 {line_num} 行JSON解析错误: {e}")
                    continue
        
        print(f"✅ 成功读取 {len(original_data):,} 条原始记录")
        
    except Exception as e:
        print(f"❌ 读取原始文件失败: {e}")
        return False
    
    # 处理数据
    print("🔄 处理数据...")
    processed_data = []
    
    for i, data in enumerate(original_data):
        if i % 10000 == 0:
            print(f"  已处理 {i:,} 条记录...")
        
        doc_id = data.get('doc_id', '')
        text = data.get('text', '')
        
        if not doc_id or not text:
            continue
        
        # 检查是否是对话数据
        if not doc_id.startswith('dialogue_'):
            continue
        
        # 解析doc_id获取flow信息
        try:
            # 移除 "dialogue_" 前缀
            remaining = doc_id[9:]
            parts = remaining.split('_')
            
            if len(parts) >= 4:
                # 重新组合flow_name
                flow_name_parts = parts[:-3]
                flow_name = "_".join(flow_name_parts)
                
                flow_id = parts[-3]
                state_id = parts[-2]
                dialogue_id = parts[-1]
                
                # 创建处理后的记录
                processed_record = {
                    'doc_id': doc_id,
                    'text': text,
                    'flow_name': flow_name,
                    'flow_id': flow_id,
                    'state_id': state_id,
                    'dialogue_id': dialogue_id
                }
                
                processed_data.append(processed_record)
            else:
                print(f"⚠️  无法解析doc_id: {doc_id}")
                
        except Exception as e:
            print(f"⚠️  处理记录失败 {doc_id}: {e}")
            continue
    
    print(f"✅ 成功处理 {len(processed_data):,} 条对话记录")
    
    # 保存处理后的数据
    print(f"💾 保存到: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in processed_data:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"✅ 保存完成: {len(processed_data):,} 条记录")
        
        # 验证保存的文件
        with open(output_file, 'r', encoding='utf-8') as f:
            saved_lines = sum(1 for _ in f)
        
        print(f"✅ 验证完成: 文件包含 {saved_lines:,} 行")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def check_original_data():
    """检查原始数据文件"""
    print("=== 检查原始数据文件 ===")
    
    possible_files = [
        "WutheringDialog/data/dialogs_zh-Hans.jsonl",
        "WutheringDialog/data/dialogs_zh-Hans.cleaned.jsonl", 
        "WutheringDialog/data/dialogs_zh-Hans.enriched.jsonl",
        "WutheringDialog/data/dialogs_zh-Hans.final.jsonl"
    ]
    
    found_files = []
    for file_path in possible_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            found_files.append((file_path, size))
            print(f"✅ 找到文件: {file_path} ({size:,} bytes)")
    
    if not found_files:
        print("❌ 没有找到原始数据文件")
        print("请确保以下文件之一存在:")
        for file_path in possible_files:
            print(f"  - {file_path}")
        return None
    
    # 选择最大的文件作为原始文件
    largest_file = max(found_files, key=lambda x: x[1])
    print(f"📁 使用文件: {largest_file[0]}")
    
    return largest_file[0]

def generate_from_any_source():
    """从任何可用的源文件生成split数据"""
    print("=== 从可用源生成Split数据 ===")
    
    # 1. 检查原始文件
    original_file = check_original_data()
    if not original_file:
        return False
    
    # 2. 如果已经是split格式，直接复制
    if 'split' in original_file:
        print("✅ 文件已经是split格式，直接使用")
        return True
    
    # 3. 生成split格式
    return generate_split_dialogue()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_original_data()
    else:
        generate_from_any_source()
