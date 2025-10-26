#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def debug_mapping():
    print("=== Debug Flow Mapping ===")
    
    # 加载PlotHandBookConfig
    with open("ConfigDB/PlotHandBookConfig.json", 'r', encoding='utf-8') as f:
        plot_config = json.load(f)
    
    print(f"PlotHandBookConfig records: {len(plot_config)}")
    
    # 显示前几个记录的flow信息
    print("\nSample flows from PlotHandBookConfig:")
    for i, item in enumerate(plot_config[:3]):
        quest_id = item.get("QuestId")
        data_str = item.get("Data", "")
        
        try:
            data_list = json.loads(data_str)
            print(f"\nQuest {quest_id}:")
            for j, flow_item in enumerate(data_list[:3]):
                flow_info = flow_item.get("Flow", {})
                flow_name = flow_info.get("FlowListName", "")
                if flow_name:
                    print(f"  Flow {j+1}: {flow_name}")
        except:
            continue
    
    # 检查对话文件中的doc_id格式
    print("\n=== Sample doc_ids from dialogue file ===")
    with open("WutheringDialog/data/dialogs_zh-Hans.split.jsonl", 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', '')
            print(f"  {doc_id}")

if __name__ == "__main__":
    debug_mapping()

