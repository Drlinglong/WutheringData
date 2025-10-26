    #!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def debug_mapping_issue():
    print("=== Debug Mapping Issue ===")
    
    # 加载QuestNodeData
    with open("ConfigDB/QuestNodeData.json", 'r', encoding='utf-8') as f:
        quest_nodes = json.load(f)
    
    # 统计所有flow名称
    all_flows = set()
    
    for node in quest_nodes:
        key = node.get("Key", "")
        data_str = node.get("Data", "")
        
        try:
            data_obj = json.loads(data_str)
            
            # 查找Flow信息
            if "Condition" in data_obj:
                condition = data_obj["Condition"]
                if "Flow" in condition:
                    flow_info = condition["Flow"]
                    flow_name = flow_info.get("FlowListName", "")
                    if flow_name:
                        all_flows.add(flow_name)
                
                # 也检查AddOptions中的Flow
                if "AddOptions" in condition:
                    for option in condition["AddOptions"]:
                        if "Option" in option and "Type" in option["Option"]:
                            option_type = option["Option"]["Type"]
                            if "Flow" in option_type:
                                flow_info = option_type["Flow"]
                                flow_name = flow_info.get("FlowListName", "")
                                if flow_name:
                                    all_flows.add(flow_name)
                                    
        except:
            continue
    
    print(f"Total unique flows found: {len(all_flows)}")
    
    # 查找包含"新剧本"的flow
    test_flows = [f for f in all_flows if "新剧本" in f]
    print(f"\nFlows containing '新剧本': {len(test_flows)}")
    for flow in test_flows:
        print(f"  {flow}")
    
    # 查找包含"剧情"的flow
    story_flows = [f for f in all_flows if "剧情" in f]
    print(f"\nFlows containing '剧情': {len(story_flows)}")
    for flow in story_flows[:10]:  # 只显示前10个
        print(f"  {flow}")
    
    # 检查对话文件中的flow名称
    print("\n=== Sample flows from dialogue file ===")
    with open("WutheringDialog/data/dialogs_zh-Hans.split.jsonl", 'r', encoding='utf-8') as f:
        dialogue_flows = set()
        for i, line in enumerate(f):
            if i >= 100:  # 只检查前100行
                break
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', '')
            
            if doc_id.startswith("dialogue_"):
                remaining = doc_id[9:]  # 移除 "dialogue_"
                parts = remaining.split('_')
                if len(parts) >= 4:
                    flow_name_parts = parts[:-3]
                    flow_name = "_".join(flow_name_parts)
                    dialogue_flows.add(flow_name)
        
        print(f"Sample dialogue flows:")
        for flow in list(dialogue_flows)[:10]:
            print(f"  {flow}")

if __name__ == "__main__":
    debug_mapping_issue()
