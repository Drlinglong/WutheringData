#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def check_split_file():
    """检查拆分后的文件格式和内容"""
    
    # 检查文件是否存在
    split_file = "WutheringDialog/data/rag_input_split.jsonl"
    if not os.path.exists(split_file):
        print(f"文件不存在: {split_file}")
        return
    
    print("=== 检查拆分后的文件 ===")
    
    # 读取并分析文件
    with open(split_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"总行数: {len(lines)}")
    
    # 检查前10个doc_id
    print("\n前10个doc_id示例:")
    for i, line in enumerate(lines[:10]):
        try:
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', 'N/A')
            print(f"  {i+1}: {doc_id}")
        except json.JSONDecodeError as e:
            print(f"  {i+1}: JSON解析错误 - {e}")
    
    # 检查doc_id格式
    print("\n=== doc_id格式分析 ===")
    character_count = 0
    weapon_count = 0
    item_count = 0
    other_count = 0
    
    for line in lines:
        try:
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', '')
            
            if doc_id.startswith('character_'):
                character_count += 1
            elif doc_id.startswith('weapon_'):
                weapon_count += 1
            elif doc_id.startswith('item_'):
                item_count += 1
            else:
                other_count += 1
                
        except json.JSONDecodeError:
            continue
    
    print(f"角色相关: {character_count}")
    print(f"武器相关: {weapon_count}")
    print(f"物品相关: {item_count}")
    print(f"其他类型: {other_count}")
    
    # 检查是否有重复的doc_id
    print("\n=== 检查重复doc_id ===")
    doc_ids = []
    duplicates = []
    
    for line in lines:
        try:
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', '')
            if doc_id in doc_ids:
                duplicates.append(doc_id)
            else:
                doc_ids.append(doc_id)
        except json.JSONDecodeError:
            continue
    
    if duplicates:
        print(f"发现重复的doc_id: {len(duplicates)}")
        for dup in duplicates[:5]:  # 只显示前5个
            print(f"  - {dup}")
    else:
        print("没有发现重复的doc_id")
    
    # 检查文本内容长度
    print("\n=== 文本内容长度分析 ===")
    text_lengths = []
    for line in lines:
        try:
            data = json.loads(line.strip())
            text = data.get('text', '')
            text_lengths.append(len(text))
        except json.JSONDecodeError:
            continue
    
    if text_lengths:
        print(f"平均文本长度: {sum(text_lengths) / len(text_lengths):.1f} 字符")
        print(f"最短文本长度: {min(text_lengths)} 字符")
        print(f"最长文本长度: {max(text_lengths)} 字符")

if __name__ == "__main__":
    check_split_file()
