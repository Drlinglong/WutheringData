#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

class CompleteDataMappingAnalyzer:
    def __init__(self):
        self.plot_handbook_config = []
        self.quest_node_data = []
        self.quest_config = []
        self.textmap_data = {}
        self.flow_config = []
        
        # 映射关系
        self.flow_to_quest_mapping = {}  # FlowListName -> QuestId
        self.quest_to_chapter_mapping = {}  # QuestId -> ChapterId
        self.quest_info_cache = {}  # QuestId -> {name, desc, chapter_info}
        self.chapter_info_cache = {}  # ChapterId -> {num, section, name}
        
    def load_all_configs(self):
        """加载所有配置文件"""
        print("Loading all configuration files...")
        
        # 加载PlotHandBookConfig
        with open("ConfigDB/PlotHandBookConfig.json", 'r', encoding='utf-8') as f:
            self.plot_handbook_config = json.load(f)
        print(f"PlotHandBookConfig: {len(self.plot_handbook_config)} records")
        
        # 加载QuestNodeData
        with open("ConfigDB/QuestNodeData.json", 'r', encoding='utf-8') as f:
            self.quest_node_data = json.load(f)
        print(f"QuestNodeData: {len(self.quest_node_data)} records")
        
        # 加载Quest
        with open("ConfigDB/Quest.json", 'r', encoding='utf-8') as f:
            self.quest_config = json.load(f)
        print(f"Quest: {len(self.quest_config)} records")
        
        # 加载TextMap
        with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
            self.textmap_data = json.load(f)
        print(f"TextMap: {len(self.textmap_data)} records")
        
        # 加载Flow
        with open("ConfigDB/Flow.json", 'r', encoding='utf-8') as f:
            self.flow_config = json.load(f)
        print(f"Flow: {len(self.flow_config)} records")
    
    def build_flow_to_quest_mapping(self):
        """建立FlowListName到QuestId的映射"""
        print("Building flow to quest mapping...")
        
        # 从PlotHandBookConfig建立映射
        plot_mappings = 0
        for item in self.plot_handbook_config:
            quest_id = item.get("QuestId")
            data_str = item.get("Data", "")
            
            try:
                data_obj = json.loads(data_str)
                for flow_item in data_obj:
                    flow_info = flow_item.get("Flow", {})
                    flow_name = flow_info.get("FlowListName", "")
                    
                    if flow_name and flow_name != "":
                        self.flow_to_quest_mapping[flow_name] = quest_id
                        plot_mappings += 1
            except (json.JSONDecodeError, ValueError):
                continue
        
        # 从QuestNodeData建立映射
        node_mappings = 0
        for item in self.quest_node_data:
            key = item.get("Key", "")
            data_str = item.get("Data", "")
            
            try:
                quest_id = int(key.split("_")[0])
                data_obj = json.loads(data_str)
                
                # 查找Flow信息
                if "Condition" in data_obj:
                    condition = data_obj["Condition"]
                    if "Flow" in condition:
                        flow_info = condition["Flow"]
                        flow_name = flow_info.get("FlowListName", "")
                        
                        if flow_name and flow_name != "":
                            self.flow_to_quest_mapping[flow_name] = quest_id
                            node_mappings += 1
                
                # 检查AddOptions中的Flow
                if "Condition" in data_obj and "AddOptions" in data_obj["Condition"]:
                    for option in data_obj["Condition"]["AddOptions"]:
                        if "Option" in option and "Type" in option["Option"]:
                            option_type = option["Option"]["Type"]
                            if "Flow" in option_type:
                                flow_info = option_type["Flow"]
                                flow_name = flow_info.get("FlowListName", "")
                                
                                if flow_name and flow_name != "":
                                    self.flow_to_quest_mapping[flow_name] = quest_id
                                    node_mappings += 1
                                    
            except (json.JSONDecodeError, ValueError):
                continue
        
        print(f"Flow mappings from PlotHandBook: {plot_mappings}")
        print(f"Flow mappings from QuestNodeData: {node_mappings}")
        print(f"Total unique flow mappings: {len(self.flow_to_quest_mapping)}")
    
    def build_quest_to_chapter_mapping(self):
        """建立QuestId到ChapterId的映射"""
        print("Building quest to chapter mapping...")
        
        # 分析QuestId模式来确定章节映射
        quest_ids = set()
        
        # 从PlotHandBookConfig收集QuestId
        for item in self.plot_handbook_config:
            quest_id = item.get("QuestId")
            if quest_id:
                quest_ids.add(quest_id)
        
        # 从QuestNodeData收集QuestId
        for item in self.quest_node_data:
            key = item.get("Key", "")
            try:
                quest_id = int(key.split("_")[0])
                quest_ids.add(quest_id)
            except ValueError:
                continue
        
        print(f"Found {len(quest_ids)} unique quest IDs")
        
        # 分析QuestId模式
        chapter_patterns = defaultdict(list)
        for quest_id in quest_ids:
            if quest_id >= 139000000 and quest_id < 140000000:
                chapter_patterns["139"].append(quest_id)
            elif quest_id >= 135000000 and quest_id < 136000000:
                chapter_patterns["135"].append(quest_id)
            elif quest_id >= 140000000 and quest_id < 141000000:
                chapter_patterns["140"].append(quest_id)
            else:
                chapter_patterns["other"].append(quest_id)
        
        print("Quest ID patterns:")
        for pattern, ids in chapter_patterns.items():
            print(f"  {pattern}: {len(ids)} quests")
            if len(ids) <= 10:
                print(f"    Examples: {sorted(ids)[:10]}")
    
    def analyze_textmap_structure(self):
        """分析TextMap的结构"""
        print("Analyzing TextMap structure...")
        
        # 分析QuestName模式
        quest_name_keys = [k for k in self.textmap_data.keys() if k.startswith("Quest_") and "_QuestName_" in k]
        print(f"QuestName keys: {len(quest_name_keys)}")
        
        # 分析QuestDesc模式
        quest_desc_keys = [k for k in self.textmap_data.keys() if k.startswith("Quest_") and "_QuestDesc_" in k]
        print(f"QuestDesc keys: {len(quest_desc_keys)}")
        
        # 分析ChildQuestTip模式
        child_tip_keys = [k for k in self.textmap_data.keys() if k.startswith("Quest_") and "_ChildQuestTip_" in k]
        print(f"ChildQuestTip keys: {len(child_tip_keys)}")
        
        # 分析Chapter模式
        chapter_keys = [k for k in self.textmap_data.keys() if k.startswith("QuestChapter_")]
        print(f"Chapter keys: {len(chapter_keys)}")
        
        # 分析QuestName后缀模式
        quest_name_suffixes = defaultdict(int)
        for key in quest_name_keys:
            parts = key.split("_")
            if len(parts) >= 4:
                suffix = f"{parts[-2]}_{parts[-1]}"
                quest_name_suffixes[suffix] += 1
        
        print("QuestName suffix patterns:")
        for suffix, count in sorted(quest_name_suffixes.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {suffix}: {count} occurrences")
    
    def analyze_dialogue_doc_id_patterns(self):
        """分析对话doc_id的模式"""
        print("Analyzing dialogue doc_id patterns...")
        
        # 读取对话文件
        dialogue_flows = set()
        doc_id_patterns = defaultdict(int)
        
        try:
            with open("WutheringDialog/data/dialogs_zh-Hans.split.jsonl", 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        doc_id = data.get('doc_id', '')
                        
                        if doc_id.startswith("dialogue_"):
                            # 解析doc_id
                            remaining = doc_id[9:]  # 移除 "dialogue_"
                            parts = remaining.split('_')
                            
                            if len(parts) >= 4:
                                flow_name_parts = parts[:-3]
                                flow_name = "_".join(flow_name_parts)
                                dialogue_flows.add(flow_name)
                                
                                # 统计模式
                                pattern = f"{len(flow_name_parts)}_parts"
                                doc_id_patterns[pattern] += 1
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            print("Dialogue file not found")
            return
        
        print(f"Unique dialogue flows: {len(dialogue_flows)}")
        print("Doc ID patterns:")
        for pattern, count in sorted(doc_id_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count} occurrences")
        
        # 检查哪些对话流在配置中有映射
        mapped_flows = 0
        unmapped_flows = set()
        
        for flow in dialogue_flows:
            if flow in self.flow_to_quest_mapping:
                mapped_flows += 1
            else:
                unmapped_flows.add(flow)
        
        print(f"Mapped dialogue flows: {mapped_flows}/{len(dialogue_flows)} ({mapped_flows/len(dialogue_flows)*100:.1f}%)")
        
        if unmapped_flows:
            print("Sample unmapped flows:")
            for flow in sorted(list(unmapped_flows))[:10]:
                print(f"  {flow}")
    
    def generate_mapping_report(self):
        """生成完整的映射报告"""
        print("\n" + "="*60)
        print("COMPLETE DATA MAPPING ANALYSIS REPORT")
        print("="*60)
        
        # 1. 配置文件统计
        print("\n1. CONFIGURATION FILES:")
        print(f"   PlotHandBookConfig: {len(self.plot_handbook_config)} records")
        print(f"   QuestNodeData: {len(self.quest_node_data)} records")
        print(f"   Quest: {len(self.quest_config)} records")
        print(f"   TextMap: {len(self.textmap_data)} records")
        print(f"   Flow: {len(self.flow_config)} records")
        
        # 2. 映射关系统计
        print(f"\n2. MAPPING RELATIONSHIPS:")
        print(f"   Flow to Quest mappings: {len(self.flow_to_quest_mapping)}")
        
        # 3. 数据覆盖度分析
        print(f"\n3. DATA COVERAGE ANALYSIS:")
        self.analyze_dialogue_doc_id_patterns()
        
        # 4. 关键发现
        print(f"\n4. KEY FINDINGS:")
        print("   - PlotHandBookConfig 主要包含主线任务的映射")
        print("   - QuestNodeData 包含更细粒度的任务节点映射")
        print("   - Quest.json 使用不同的ID系统，与PlotHandBookConfig不匹配")
        print("   - TextMap 中的QuestName/QuestDesc有多种后缀格式")
        print("   - 对话文件包含大量测试数据和NPC对话，不在配置文件中")
        
        # 5. 建议的解决方案
        print(f"\n5. RECOMMENDED SOLUTION:")
        print("   - 使用QuestNodeData作为主要映射源（覆盖更全面）")
        print("   - 动态查找TextMap中的QuestName/QuestDesc（支持多种后缀）")
        print("   - 建立QuestId到ChapterId的智能映射")
        print("   - 对于未映射的对话流，提供默认值或跳过处理")
    
    def run_complete_analysis(self):
        """运行完整分析"""
        print("=== COMPLETE DATA MAPPING ANALYSIS ===")
        
        # 加载所有配置
        self.load_all_configs()
        
        # 建立映射关系
        self.build_flow_to_quest_mapping()
        self.build_quest_to_chapter_mapping()
        
        # 分析结构
        self.analyze_textmap_structure()
        
        # 生成报告
        self.generate_mapping_report()

if __name__ == "__main__":
    analyzer = CompleteDataMappingAnalyzer()
    analyzer.run_complete_analysis()
