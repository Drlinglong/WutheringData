#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from typing import Dict, List, Tuple, Optional

class CorrectDialogueProcessor:
    def __init__(self):
        self.quest_node_data = {}
        self.quest_data = {}
        self.textmap_data = {}
        self.flow_to_quest_mapping = {}
        
    def load_config_files(self):
        """加载所有配置文件"""
        print("Loading configuration files...")
        
        # 加载QuestNodeData.json
        with open("ConfigDB/QuestNodeData.json", 'r', encoding='utf-8') as f:
            self.quest_node_data = json.load(f)
        print(f"QuestNodeData loaded: {len(self.quest_node_data)} records")
        
        # 加载Quest.json
        with open("ConfigDB/Quest.json", 'r', encoding='utf-8') as f:
            self.quest_data = json.load(f)
        print(f"Quest loaded: {len(self.quest_data)} records")
        
        # 加载TextMap
        with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
            self.textmap_data = json.load(f)
        print(f"TextMap loaded: {len(self.textmap_data)} records")
    
    def build_flow_to_quest_mapping(self):
        """建立对话流到任务的映射"""
        print("Building flow to quest mapping...")
        
        mapped_flows = 0
        
        # 从QuestNodeData.json建立映射
        for node_item in self.quest_node_data:
            key = node_item.get("Key", "")
            data_str = node_item.get("Data", "")
            
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
                        
                        if flow_name and flow_name != "":
                            # 建立映射: flow_name -> quest_id
                            self.flow_to_quest_mapping[flow_name] = quest_id
                            mapped_flows += 1
                
                # 也检查AddOptions中的Flow
                if "Condition" in data_obj and "AddOptions" in data_obj["Condition"]:
                    for option in data_obj["Condition"]["AddOptions"]:
                        if "Option" in option and "Type" in option["Option"]:
                            option_type = option["Option"]["Type"]
                            if "Flow" in option_type:
                                flow_info = option_type["Flow"]
                                flow_name = flow_info.get("FlowListName", "")
                                
                                if flow_name and flow_name != "":
                                    self.flow_to_quest_mapping[flow_name] = quest_id
                                    mapped_flows += 1
                                    
            except (json.JSONDecodeError, ValueError) as e:
                continue
        
        print(f"Mapped {mapped_flows} flows to quests")
        print(f"Total flow mappings: {len(self.flow_to_quest_mapping)}")
        
        # 显示一些示例映射
        print("\nSample mappings:")
        for i, (flow_name, quest_id) in enumerate(list(self.flow_to_quest_mapping.items())[:5]):
            print(f"  {flow_name} -> Quest {quest_id}")
    
    def get_quest_info(self, quest_id: int) -> Dict[str, str]:
        """获取任务信息"""
        quest_info = {
            'quest_name': '',
            'quest_desc': '',
            'chapter_title': '',
            'chapter_desc': ''
        }
        
        # 从Quest.json查找任务信息
        for quest in self.quest_data:
            if quest.get("Id") == quest_id:
                quest_info['quest_name'] = quest.get("QuestName", "")
                quest_info['quest_desc'] = quest.get("QuestText", "")
                break
        
        # 从TextMap查找章节信息
        for key, value in self.textmap_data.items():
            if key.startswith(f"QuestChapter_{quest_id}_"):
                if "ChapterName" in key:
                    quest_info['chapter_title'] = value
                elif "ChapterNum" in key:
                    quest_info['chapter_desc'] = value
        
        return quest_info
    
    def parse_dialogue_doc_id(self, doc_id: str) -> Dict[str, str]:
        """正确解析对话doc_id"""
        # 格式: dialogue_剧情_中曲台地_NPC对话_19_1_0
        # 应该解析为: dialogue + 剧情_中曲台地_NPC对话 + 19 + 1 + 0
        
        if not doc_id.startswith("dialogue_"):
            return {}
        
        # 移除 "dialogue_" 前缀
        remaining = doc_id[9:]  # 移除 "dialogue_"
        
        # 分割剩余部分
        parts = remaining.split('_')
        
        if len(parts) >= 4:
            # 重新组合flow_name
            flow_name_parts = parts[:-3]  # 除了最后3个部分
            flow_name = "_".join(flow_name_parts)
            
            flow_id = parts[-3]
            state_id = parts[-2] 
            dialogue_id = parts[-1]
            
            return {
                'flow_name': flow_name,
                'flow_id': flow_id,
                'state_id': state_id,
                'dialogue_id': dialogue_id
            }
        
        return {}
    
    def process_dialogue_data(self, input_file: str, output_file: str):
        """处理对话数据"""
        print(f"Processing dialogue data from {input_file}...")
        
        processed_count = 0
        mapped_count = 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Reading {len(lines)} dialogue lines...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, line in enumerate(lines):
                if i % 5000 == 0:
                    print(f"Progress: {i}/{len(lines)}")
                
                try:
                    data = json.loads(line.strip())
                    doc_id = data.get('doc_id', '')
                    text = data.get('text', '')
                    
                    # 正确解析doc_id
                    doc_info = self.parse_dialogue_doc_id(doc_id)
                    if not doc_info:
                        continue
                    
                    flow_name = doc_info['flow_name']
                    
                    # 查找对应的quest_id
                    quest_id = self.flow_to_quest_mapping.get(flow_name)
                    
                    if quest_id:
                        mapped_count += 1
                        quest_info = self.get_quest_info(quest_id)
                        
                        # 构建最终数据
                        final_item = {
                            'doc_id': doc_id,
                            'quest_id': quest_id,
                            'quest_name': quest_info['quest_name'],
                            'quest_desc': quest_info['quest_desc'],
                            'chapter_title': quest_info['chapter_title'],
                            'chapter_desc': quest_info['chapter_desc'],
                            'section_title': flow_name,
                            'section_desc': '',
                            'flow_id': doc_info['flow_id'],
                            'state_id': doc_info['state_id'],
                            'dialogue_id': doc_info['dialogue_id'],
                            'text': text
                        }
                    else:
                        # 没有找到映射的情况
                        final_item = {
                            'doc_id': doc_id,
                            'quest_id': None,
                            'quest_name': 'Unknown',
                            'quest_desc': 'Unknown',
                            'chapter_title': 'Unknown',
                            'chapter_desc': 'Unknown',
                            'section_title': flow_name,
                            'section_desc': '',
                            'flow_id': doc_info['flow_id'],
                            'state_id': doc_info['state_id'],
                            'dialogue_id': doc_info['dialogue_id'],
                            'text': text
                        }
                    
                    f.write(json.dumps(final_item, ensure_ascii=False) + '\n')
                    processed_count += 1
                    
                except json.JSONDecodeError as e:
                    print(f"Line {i+1} JSON error: {e}")
                    continue
        
        print(f"Processing complete!")
        print(f"Total processed: {processed_count}")
        print(f"Successfully mapped: {mapped_count}")
        print(f"Mapping rate: {mapped_count/processed_count*100:.1f}%")
    
    def run(self):
        """运行完整处理流程"""
        print("=== Correct Dialogue Data Processor ===")
        
        # 加载配置文件
        self.load_config_files()
        
        # 建立映射
        self.build_flow_to_quest_mapping()
        
        # 处理对话数据
        input_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
        output_file = "WutheringDialog/data/dialogs_zh-Hans.corrected.jsonl"
        
        self.process_dialogue_data(input_file, output_file)
        
        print(f"\nCorrected dataset saved to: {output_file}")

if __name__ == "__main__":
    processor = CorrectDialogueProcessor()
    processor.run()

