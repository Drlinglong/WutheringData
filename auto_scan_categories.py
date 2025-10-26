#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from collections import defaultdict, Counter

def scan_all_dialogue_categories():
    """自动扫描所有对话类型并生成分类"""
    
    # 读取对话文件
    dialogue_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
    
    # 统计所有flow_name模式
    flow_patterns = defaultdict(int)
    unknown_flows = defaultdict(int)
    
    print("Scanning all dialogue flow patterns...")
    
    with open(dialogue_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line_num % 10000 == 0:
                print(f"Processed {line_num} lines...")
            
            try:
                data = json.loads(line.strip())
                doc_id = data.get('doc_id', '')
                
                if not doc_id.startswith("dialogue_"):
                    continue
                
                # 解析flow_name
                remaining = doc_id[9:]  # 移除 "dialogue_" 前缀
                parts = remaining.split('_')
                
                if len(parts) >= 4:
                    # 重新组合flow_name
                    flow_name_parts = parts[:-3]
                    flow_name = "_".join(flow_name_parts)
                    flow_patterns[flow_name] += 1
                else:
                    unknown_flows[remaining] += 1
                    
            except json.JSONDecodeError:
                continue
    
    print(f"\nFound {len(flow_patterns)} unique flow patterns")
    print(f"Found {len(unknown_flows)} unknown patterns")
    
    # 按出现频率排序
    sorted_flows = sorted(flow_patterns.items(), key=lambda x: x[1], reverse=True)
    
    print("\n=== TOP 50 MOST COMMON FLOW PATTERNS ===")
    for i, (flow, count) in enumerate(sorted_flows[:50]):
        print(f"{i+1:2d}. {flow} ({count} dialogues)")
    
    # 分析模式并生成分类
    print("\n=== GENERATING CATEGORIES ===")
    
    # 生态对话模式
    ecological_patterns = []
    character_patterns = []
    main_story_patterns = []
    side_quest_patterns = []
    special_patterns = []
    
    for flow, count in sorted_flows:
        flow_lower = flow.lower()
        
        # 生态对话
        if any(keyword in flow for keyword in ['生态', 'NPC', '冒泡', '氛围', '配音', '七丘', '要塞', '广场', '营地']):
            ecological_patterns.append((flow, count))
        
        # 角色对话
        elif any(keyword in flow for keyword in ['角色', '线', '副本', 'V2.3', '夏空', '赞妮', '吟霖', '忌炎', '散华', '白芷']):
            character_patterns.append((flow, count))
        
        # 主线剧情
        elif any(keyword in flow for keyword in ['主线', '剧情', '巴别塔', '狄斯台地', '赤林台地', '2_4', '2_6']):
            main_story_patterns.append((flow, count))
        
        # 支线任务
        elif any(keyword in flow for keyword in ['支线', '团团', '记忆手册', '布偶', '猫猫', '灯塔', '沉没']):
            side_quest_patterns.append((flow, count))
        
        # 特殊类型
        elif any(keyword in flow for keyword in ['测试', '玩法', '活动', '副本']):
            special_patterns.append((flow, count))
    
    # 生成分类代码
    print("\n=== ECOLOGICAL CATEGORIES ===")
    for flow, count in ecological_patterns[:20]:  # 显示前20个
        print(f"'{flow}': {{'chapter': '瑝珑 第二章', 'section': '{flow}生态'}},")
    
    print("\n=== CHARACTER CATEGORIES ===")
    for flow, count in character_patterns[:15]:  # 显示前15个
        print(f"'{flow}': {{'chapter': '瑝珑 第一章', 'section': '{flow}角色线'}},")
    
    print("\n=== MAIN STORY CATEGORIES ===")
    for flow, count in main_story_patterns[:15]:  # 显示前15个
        print(f"'{flow}': {{'chapter': '瑝珑 第二章', 'section': '{flow}主线'}},")
    
    print("\n=== SIDE QUEST CATEGORIES ===")
    for flow, count in side_quest_patterns[:15]:  # 显示前15个
        print(f"'{flow}': {{'chapter': '瑝珑 第一章', 'section': '{flow}支线'}},")
    
    print("\n=== SPECIAL CATEGORIES ===")
    for flow, count in special_patterns[:10]:  # 显示前10个
        print(f"'{flow}': {{'chapter': '特殊内容', 'section': '{flow}对话'}},")
    
    # 统计未分类的
    print(f"\n=== UNCLASSIFIED PATTERNS (showing top 20) ===")
    classified_flows = set()
    for patterns in [ecological_patterns, character_patterns, main_story_patterns, side_quest_patterns, special_patterns]:
        for flow, _ in patterns:
            classified_flows.add(flow)
    
    unclassified = [(flow, count) for flow, count in sorted_flows if flow not in classified_flows]
    for flow, count in unclassified[:20]:
        print(f"'{flow}': {{'chapter': '未分类', 'section': '{flow}'}},")
    
    print(f"\nTotal unclassified patterns: {len(unclassified)}")
    
    return {
        'ecological': ecological_patterns,
        'character': character_patterns, 
        'main_story': main_story_patterns,
        'side_quest': side_quest_patterns,
        'special': special_patterns,
        'unclassified': unclassified
    }

if __name__ == "__main__":
    scan_all_dialogue_categories()
