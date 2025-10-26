#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def analyze_quest_name_issue():
    print("=== Analyzing Quest Name Issue ===")
    
    # 加载数据
    with open("WutheringDialog/data/dialogs_zh-Hans.ultimate.jsonl", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data = [json.loads(line) for line in lines]
    mapped = [d for d in data if d['quest_id'] is not None]
    empty_name = [d for d in mapped if d['quest_name'] == '']
    
    print(f"Total records: {len(data)}")
    print(f"Mapped records: {len(mapped)}")
    print(f"Empty quest_name: {len(empty_name)}")
    print(f"Empty quest_name rate: {len(empty_name)/len(mapped)*100:.1f}%")
    
    # 分析quest_id分布
    quest_ids = set(d['quest_id'] for d in mapped)
    print(f"\nUnique quest_ids: {len(quest_ids)}")
    
    # 检查前几个quest_id
    print("\nSample quest_ids:")
    for quest_id in sorted(list(quest_ids))[:10]:
        count = len([d for d in mapped if d['quest_id'] == quest_id])
        empty_count = len([d for d in empty_name if d['quest_id'] == quest_id])
        print(f"  Quest {quest_id}: {count} records, {empty_count} empty names")
    
    # 检查TextMap中是否有这些quest_id的信息
    print("\n=== Checking TextMap for Quest Names ===")
    with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
        textmap = json.load(f)
    
    for quest_id in sorted(list(quest_ids))[:5]:
        # 查找所有可能的QuestName格式
        possible_keys = [
            f"Quest_{quest_id}_QuestName_0_2",
            f"Quest_{quest_id}_QuestName_886_1",
            f"Quest_{quest_id}_QuestName_0_1",
            f"Quest_{quest_id}_QuestName_1_1",
        ]
        
        found_keys = []
        for key in possible_keys:
            if key in textmap:
                found_keys.append(f"{key}: {textmap[key]}")
        
        print(f"\nQuest {quest_id}:")
        if found_keys:
            for key_info in found_keys:
                print(f"  {key_info}")
        else:
            print("  No QuestName found")
            
            # 查找所有包含这个quest_id的key
            quest_keys = [k for k in textmap.keys() if f"Quest_{quest_id}_" in k]
            print(f"  Found {len(quest_keys)} keys with Quest_{quest_id}_")
            if quest_keys:
                print(f"  Sample keys: {quest_keys[:3]}")

if __name__ == "__main__":
    analyze_quest_name_issue()

