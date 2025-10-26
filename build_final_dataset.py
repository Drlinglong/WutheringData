#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from typing import Dict, List, Tuple, Optional

class FinalDialogueProcessor:
    def __init__(self):
        self.plot_config = {}
        self.quest_node_data = {}
        self.quest_data = {}
        self.textmap_data = {}
        self.flow_to_quest_mapping = {}
        
    def load_config_files(self):
        """加载所有配置文件"""
        print("Loading configuration files...")
        
        # 加载PlotHandBookConfig.json
        with open("ConfigDB/PlotHandBookConfig.json", 'r', encoding='utf-8') as f:
            self.plot_config = json.load(f)
        print(f"PlotHandBookConfig loaded: {len(self.plot_config)} records")
        
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
        
        # 从PlotHandBookConfig.json建立映射
        for plot_item in self.plot_config:
            quest_id = plot_item.get("QuestId")
            data_str = plot_item.get("Data", "")
            
            try:
                data_list = json.loads(data_str)
                for item in data_list:
                    flow_info = item.get("Flow", {})
                    flow_name = flow_info.get("FlowListName", "")
                    
                    if flow_name and flow_name != "":
                        # 建立映射: flow_name -> quest_id
                        self.flow_to_quest_mapping[flow_name] = quest_id
                        mapped_flows += 1
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing PlotHandBookConfig data: {e}")
                continue
        
        # 从QuestNodeData.json建立映射
        for node_item in self.quest_node_data:
            key = node_item.get("Key", "")
            data_str = node_item.get("Data", "")
            
            try:
                data_obj = json.loads(data_str)
                
                # 查找Flow信息
                if "Condition" in data_obj:
                    condition = data_obj["Condition"]
                    if "AddOptions" in condition:
                        for option in condition["AddOptions"]:
                            if "Option" in option:
                                option_data = option["Option"]
                                if "Type" in option_data and "Flow" in option_data["Type"]:
                                    flow_info = option_data["Type"]["Flow"]
                                    flow_name = flow_info.get("FlowListName", "")
                                    
                                    if flow_name and flow_name != "":
                                        # 从key提取quest_id
                                        quest_id = int(key.split("_")[0])
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
        """解析对话doc_id"""
        # 格式: dialogue_剧情_新剧本测试_1_1_0
        parts = doc_id.split('_')
        if len(parts) >= 6:
            return {
                'quest_type': parts[1],
                'quest_name': parts[2], 
                'quest_id': parts[3],
                'section_id': parts[4],
                'dialogue_id': parts[5]
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
                    
                    # 解析doc_id
                    doc_info = self.parse_dialogue_doc_id(doc_id)
                    if not doc_info:
                        continue
                    
                    # 构建flow_name来查找映射
                    flow_name = f"{doc_info['quest_type']}_{doc_info['quest_name']}"
                    
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
                            'section_title': flow_name,  # 使用flow_name作为section_title
                            'section_desc': '',  # 暂时留空
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
        print("=== Final Dialogue Data Processor ===")
        
        # 加载配置文件
        self.load_config_files()
        
        # 建立映射
        self.build_flow_to_quest_mapping()
        
        # 处理对话数据
        input_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
        output_file = "WutheringDialog/data/dialogs_zh-Hans.final.jsonl"
        
        self.process_dialogue_data(input_file, output_file)
        
        print(f"\nFinal dataset saved to: {output_file}")

if __name__ == "__main__":
    processor = FinalDialogueProcessor()
    processor.run()