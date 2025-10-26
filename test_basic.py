#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def test_basic_functionality():
    print("=== 测试基本功能 ===")
    
    # 检查文件
    textmap_file = "TextMap/zh-Hans/MultiText.json"
    dialogue_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
    
    print(f"TextMap文件存在: {os.path.exists(textmap_file)}")
    print(f"对话文件存在: {os.path.exists(dialogue_file)}")
    
    # 测试读取TextMap
    print("\n=== 测试读取TextMap ===")
    try:
        with open(textmap_file, 'r', encoding='utf-8') as f:
            textmap_data = json.load(f)
        print(f"TextMap加载成功，共 {len(textmap_data)} 条记录")
        
        # 查找你提到的关键信息
        target_keys = [
            "QuestChapter_1_ChapterNum",
            "QuestChapter_1_SectionNum", 
            "Quest_139000025_QuestDesc_0_2",
            "Quest_139000025_ChildQuestTip_0_48"
        ]
        
        print("\n查找关键信息:")
        for key in target_keys:
            if key in textmap_data:
                print(f"  {key}: {textmap_data[key]}")
            else:
                print(f"  {key}: 未找到")
                
    except Exception as e:
        print(f"TextMap读取失败: {e}")
    
    # 测试读取对话文件
    print("\n=== 测试读取对话文件 ===")
    try:
        with open(dialogue_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"对话文件读取成功，共 {len(lines)} 行")
        
        # 显示前3行
        print("\n前3行内容:")
        for i, line in enumerate(lines[:3]):
            data = json.loads(line.strip())
            print(f"  {i+1}: {data['doc_id']} -> {data['text'][:50]}...")
            
    except Exception as e:
        print(f"对话文件读取失败: {e}")

if __name__ == "__main__":
    test_basic_functionality()

