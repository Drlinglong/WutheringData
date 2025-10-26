#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from typing import Dict, List, Tuple, Optional

class FinalCorrectProcessor:
    def __init__(self):
        self.quest_node_data = {}
        self.textmap_data = {}
        self.flow_to_quest_mapping = {}
        self.quest_to_chapter_mapping = {}
        
    def load_config_files(self):
        """加载所有配置文件"""
        print("Loading configuration files...")
        
        # 加载QuestNodeData.json
        with open("ConfigDB/QuestNodeData.json", 'r', encoding='utf-8') as f:
            self.quest_node_data = json.load(f)
        print(f"QuestNodeData loaded: {len(self.quest_node_data)} records")
        
        # 加载TextMap
        with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
            self.textmap_data = json.load(f)
        print(f"TextMap loaded: {len(self.textmap_data)} records")
    
    def build_quest_to_chapter_mapping(self):
        """建立Quest ID到Chapter ID的映射"""
        print("Building quest to chapter mapping...")
        
        # 从TextMap中查找QuestChapter信息
        chapter_info = {}
        for key, value in self.textmap_data.items():
            if key.startswith("QuestChapter_"):
                parts = key.split("_")
                if len(parts) >= 4:
                    chapter_id = parts[1]
                    field = parts[3]
                    
                    if chapter_id not in chapter_info:
                        chapter_info[chapter_id] = {}
                    chapter_info[chapter_id][field] = value
        
        print(f"Found {len(chapter_info)} chapters")
        
        # 建立Quest到Chapter的映射
        # 这里需要根据实际的数据结构来建立映射
        # 暂时使用简单的映射：139000025 -> Chapter 1
        self.quest_to_chapter_mapping = {
            139000025: 1,  # 万象新声·上 -> 世界之初
            139000026: 1,  # 可能也是第一章
            139000027: 1,  # 可能也是第一章
            # 可以根据需要添加更多映射
        }
        
        print(f"Built {len(self.quest_to_chapter_mapping)} quest to chapter mappings")
    
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
    
    def get_quest_info(self, quest_id: int) -> Dict[str, str]:
        """获取任务信息"""
        quest_info = {
            'quest_name': '',
            'quest_desc': '',
            'chapter_title': '',
            'chapter_desc': '',
            'section_title': '',
            'section_desc': ''
        }
        
        # 从TextMap查找任务信息
        quest_name_key = f"Quest_{quest_id}_QuestName_0_2"
        quest_desc_key = f"Quest_{quest_id}_QuestDesc_0_2"
        
        if quest_name_key in self.textmap_data:
            quest_info['quest_name'] = self.textmap_data[quest_name_key]
        if quest_desc_key in self.textmap_data:
            quest_info['quest_desc'] = self.textmap_data[quest_desc_key]
        
        # 获取章节信息
        chapter_id = self.quest_to_chapter_mapping.get(quest_id)
        if chapter_id:
            chapter_num_key = f"QuestChapter_{chapter_id}_ChapterNum"
            section_num_key = f"QuestChapter_{chapter_id}_SectionNum"
            chapter_name_key = f"QuestChapter_{chapter_id}_ChapterName"
            
            if chapter_num_key in self.textmap_data:
                quest_info['chapter_title'] = self.textmap_data[chapter_num_key]
            if section_num_key in self.textmap_data:
                quest_info['chapter_desc'] = self.textmap_data[section_num_key]
            if chapter_name_key in self.textmap_data:
                quest_info['section_title'] = self.textmap_data[chapter_name_key]
        
        return quest_info
    
    def get_child_tip(self, quest_id: int, dialogue_id: str) -> str:
        """获取子任务提示"""
        child_tip_key = f"Quest_{quest_id}_ChildQuestTip_0_{dialogue_id}"
        return self.textmap_data.get(child_tip_key, "")
    
    def parse_dialogue_doc_id(self, doc_id: str) -> Dict[str, str]:
        """正确解析对话doc_id"""
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
                        child_tip = self.get_child_tip(quest_id, doc_info['dialogue_id'])
                        
                        # 构建最终数据
                        final_item = {
                            'doc_id': doc_id,
                            'quest_id': quest_id,
                            'quest_name': quest_info['quest_name'],
                            'quest_desc': quest_info['quest_desc'],
                            'chapter_title': quest_info['chapter_title'],
                            'chapter_desc': quest_info['chapter_desc'],
                            'section_title': quest_info['section_title'],
                            'section_desc': child_tip,  # 使用child_tip作为section_desc
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
                            'section_title': 'Unknown',
                            'section_desc': 'Unknown',
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
        print("=== Final Correct Dialogue Processor ===")
        
        # 加载配置文件
        self.load_config_files()
        
        # 建立映射
        self.build_quest_to_chapter_mapping()
        self.build_flow_to_quest_mapping()
        
        # 处理对话数据
        input_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
        output_file = "WutheringDialog/data/dialogs_zh-Hans.final_correct.jsonl"
        
        self.process_dialogue_data(input_file, output_file)
        
        print(f"\nFinal corrected dataset saved to: {output_file}")

if __name__ == "__main__":
    processor = FinalCorrectProcessor()
    processor.run()

