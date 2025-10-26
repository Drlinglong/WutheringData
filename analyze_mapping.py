#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

def analyze_quest_mapping():
    print("=== Analyzing Quest Mapping ===")
    
    # 加载QuestNodeData
    with open("ConfigDB/QuestNodeData.json", 'r', encoding='utf-8') as f:
        quest_nodes = json.load(f)
    
    print(f"QuestNodeData records: {len(quest_nodes)}")
    
    # 查找包含"中曲台地_NPC对话"的记录
    target_flows = []
    
    for node in quest_nodes:
        key = node.get("Key", "")
        data_str = node.get("Data", "")
        
        if "中曲台地_NPC对话" in data_str:
            try:
                data_obj = json.loads(data_str)
                
                # 提取quest_id
                quest_id = int(key.split("_")[0])
                
                # 查找Flow信息
                flow_name = ""
                if "Condition" in data_obj:
                    condition = data_obj["Condition"]
                    if "Flow" in condition:
                        flow_info = condition["Flow"]
                        flow_name = flow_info.get("FlowListName", "")
                
                target_flows.append({
                    'quest_id': quest_id,
                    'flow_name': flow_name,
                    'key': key
                })
                
            except (json.JSONDecodeError, ValueError) as e:
                continue
    
    print(f"\nFound {len(target_flows)} records with '中曲台地_NPC对话':")
    for flow in target_flows:
        print(f"  Quest {flow['quest_id']}: {flow['flow_name']} (Key: {flow['key']})")
    
    # 检查对话文件中的doc_id格式
    print("\n=== Sample doc_ids from dialogue file ===")
    with open("WutheringDialog/data/dialogs_zh-Hans.split.jsonl", 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', '')
            
            # 解析doc_id
            parts = doc_id.split('_')
            if len(parts) >= 6:
                quest_type = parts[1]
                quest_name = parts[2]
                quest_id = parts[3]
                section_id = parts[4]
                dialogue_id = parts[5]
                
                print(f"  {doc_id}")
                print(f"    -> quest_type: {quest_type}")
                print(f"    -> quest_name: {quest_name}")
                print(f"    -> quest_id: {quest_id}")
                print(f"    -> section_id: {section_id}")
                print(f"    -> dialogue_id: {dialogue_id}")
                print()

if __name__ == "__main__":
    analyze_quest_mapping()

