#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

class UltimateDialogueProcessor:
    """
    终极版对话处理器 - 修复所有映射问题包括支线任务
    """
    
    def __init__(self):
        # 配置文件数据
        self.plot_handbook_config = []
        self.quest_node_data = []
        self.textmap_data = {}
        
        # 映射缓存
        self.flow_to_quest_mapping = {}
        self.quest_info_cache = {}
        self.chapter_info_cache = {}
        
        # 精确的FlowId+StateId到ChildQuestTip的映射
        self.flow_state_to_tip_mapping = {}
        
        # 对话内容到正确描述的映射（使用部分匹配）
        self.dialogue_content_patterns = [
            {
                'pattern': r'.*何昌他也是夜归的士兵.*没能救回来.*',
                'description': '你了解到晋陆在归魂互助会再次见到了自己去世的战友何昌，所以选择留在了这里。'
            }
        ]
        
        # 生态NPC对话的默认分类
        self.ecological_categories = {
            '中曲生态': {'chapter': '瑝珑 第一章', 'section': '中曲台地生态'},
            '虎口生态': {'chapter': '瑝珑 第一章', 'section': '虎口矿场生态'},
            '荒石生态': {'chapter': '瑝珑 第一章', 'section': '荒石高地生态'},
            '天城生态': {'chapter': '瑝珑 第一章', 'section': '今州城生态'},
            '北落野生态': {'chapter': '瑝珑 第一章', 'section': '北落野生态'},
            '乘宵山': {'chapter': '瑝珑 第一章', 'section': '乘宵山虹镇生态'},
        }
        
        # 角色任务对话的分类
        self.character_categories = {
            '余果': {'chapter': '瑝珑 第一章', 'section': '角色任务对话'},
            '刘梦蝶': {'chapter': '瑝珑 第一章', 'section': '角色任务对话'},
            '寸草心': {'chapter': '瑝珑 第一章', 'section': '角色任务对话'},
            '忌炎线': {'chapter': '瑝珑 第一章', 'section': '忌炎角色线'},
            '吟霖线': {'chapter': '瑝珑 第一章', 'section': '吟霖角色线'},
            '散华线': {'chapter': '瑝珑 第一章', 'section': '散华角色线'},
            '白芷线': {'chapter': '瑝珑 第一章', 'section': '白芷角色线'},
        }
        
        # 支线任务的分类
        self.side_quest_categories = {
            '支线': {'chapter': '瑝珑 第一章', 'section': '支线任务'},
            '布偶小队历险记': {'chapter': '瑝珑 第一章', 'section': '布偶小队历险记'},
            '猫猫咖啡厅': {'chapter': '瑝珑 第一章', 'section': '猫猫咖啡厅'},
            '灯塔迷航': {'chapter': '瑝珑 第一章', 'section': '灯塔迷航'},
            '沉没的历史': {'chapter': '瑝珑 第一章', 'section': '沉没的历史'},
        }
        
        # 其他特殊分类
        self.special_categories = {
            '测试': {'chapter': '测试内容', 'section': '测试对话'},
            '玩法': {'chapter': '游戏玩法', 'section': '玩法对话'},
            '活动': {'chapter': '限时活动', 'section': '活动对话'},
            '副本': {'chapter': '副本内容', 'section': '副本对话'},
            '任务专用冒泡': {'chapter': '瑝珑 第一章', 'section': '角色任务对话'},
        }
        
        # 统计信息
        self.stats = {
            'total_dialogues': 0,
            'mapped_dialogues': 0,
            'quest_name_found': 0,
            'quest_desc_found': 0,
            'chapter_info_found': 0,
            'child_tip_found': 0,
            'exact_flow_state_mapping': 0,
            'content_mapping_found': 0,
            'ecological_mapped': 0,
            'character_mapped': 0,
            'side_quest_mapped': 0,
            'special_mapped': 0
        }
    
    def load_configurations(self):
        """加载所有必要的配置文件"""
        print("Loading configuration files...")
        
        with open("ConfigDB/PlotHandBookConfig.json", 'r', encoding='utf-8') as f:
            self.plot_handbook_config = json.load(f)
        
        with open("ConfigDB/QuestNodeData.json", 'r', encoding='utf-8') as f:
            self.quest_node_data = json.load(f)
        
        with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
            self.textmap_data = json.load(f)
        
        print(f"Loaded {len(self.plot_handbook_config)} PlotHandBook records")
        print(f"Loaded {len(self.quest_node_data)} QuestNodeData records")
        print(f"Loaded {len(self.textmap_data)} TextMap records")
    
    def build_comprehensive_mapping(self):
        """建立全面的映射关系"""
        print("Building comprehensive mapping...")
        
        # 1. 从PlotHandBookConfig建立映射
        plot_mappings = 0
        for item in self.plot_handbook_config:
            quest_id = item.get("QuestId")
            data_str = item.get("Data", "")
            
            try:
                data_obj = json.loads(data_str)
                for flow_item in data_obj:
                    flow_info = flow_item.get("Flow", {})
                    flow_name = flow_info.get("FlowListName", "")
                    flow_id = flow_info.get("FlowId", 0)
                    state_id = flow_info.get("StateId", 0)
                    
                    if flow_name and flow_name != "":
                        self.flow_to_quest_mapping[flow_name] = quest_id
                        plot_mappings += 1
                        
                        # 建立精确的FlowId+StateId映射
                        if flow_id > 0 and state_id > 0:
                            key = f"{flow_name}_{flow_id}_{state_id}"
                            self.flow_state_to_tip_mapping[key] = {
                                'quest_id': quest_id,
                                'flow_id': flow_id,
                                'state_id': state_id
                            }
            except (json.JSONDecodeError, ValueError):
                continue
        
        # 2. 从QuestNodeData建立映射（更全面）
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
                        flow_id = flow_info.get("FlowId", 0)
                        state_id = flow_info.get("StateId", 0)
                        
                        if flow_name and flow_name != "":
                            self.flow_to_quest_mapping[flow_name] = quest_id
                            node_mappings += 1
                            
                            # 建立精确的FlowId+StateId映射
                            if flow_id > 0 and state_id > 0:
                                key = f"{flow_name}_{flow_id}_{state_id}"
                                self.flow_state_to_tip_mapping[key] = {
                                    'quest_id': quest_id,
                                    'flow_id': flow_id,
                                    'state_id': state_id
                                }
                
                # 检查AddOptions中的Flow
                if "Condition" in data_obj and "AddOptions" in data_obj["Condition"]:
                    for option in data_obj["Condition"]["AddOptions"]:
                        if "Option" in option and "Type" in option["Option"]:
                            option_type = option["Option"]["Type"]
                            if "Flow" in option_type:
                                flow_info = option_type["Flow"]
                                flow_name = flow_info.get("FlowListName", "")
                                flow_id = flow_info.get("FlowId", 0)
                                state_id = flow_info.get("StateId", 0)
                                
                                if flow_name and flow_name != "":
                                    self.flow_to_quest_mapping[flow_name] = quest_id
                                    node_mappings += 1
                                    
                                    # 建立精确的FlowId+StateId映射
                                    if flow_id > 0 and state_id > 0:
                                        key = f"{flow_name}_{flow_id}_{state_id}"
                                        self.flow_state_to_tip_mapping[key] = {
                                            'quest_id': quest_id,
                                            'flow_id': flow_id,
                                            'state_id': state_id
                                        }
                                    
            except (json.JSONDecodeError, ValueError):
                continue
        
        print(f"Built {len(self.flow_to_quest_mapping)} unique flow mappings")
        print(f"Built {len(self.flow_state_to_tip_mapping)} precise flow+state mappings")
        print(f"  - From PlotHandBook: {plot_mappings}")
        print(f"  - From QuestNodeData: {node_mappings}")
    
    def get_comprehensive_quest_info(self, quest_id: int) -> Dict[str, str]:
        """获取全面的任务信息（支持多种后缀格式）"""
        if quest_id in self.quest_info_cache:
            return self.quest_info_cache[quest_id]
        
        quest_info = {
            'quest_name': '',
            'quest_desc': '',
            'chapter_title': '',
            'chapter_desc': '',
            'section_title': '',
            'section_desc': ''
        }
        
        # 动态查找QuestName（支持多种后缀）
        quest_name_keys = [k for k in self.textmap_data.keys() 
                          if k.startswith(f"Quest_{quest_id}_QuestName_")]
        if quest_name_keys:
            quest_info['quest_name'] = self.textmap_data[quest_name_keys[0]]
            quest_info['section_title'] = quest_info['quest_name']  # section_title应该是quest_name
            self.stats['quest_name_found'] += 1
        
        # 动态查找QuestDesc（支持多种后缀）
        quest_desc_keys = [k for k in self.textmap_data.keys() 
                          if k.startswith(f"Quest_{quest_id}_QuestDesc_")]
        if quest_desc_keys:
            quest_info['quest_desc'] = self.textmap_data[quest_desc_keys[0]]
            self.stats['quest_desc_found'] += 1
        
        # 查找章节信息
        chapter_info = self.get_comprehensive_chapter_info(quest_id)
        quest_info.update(chapter_info)
        
        # 缓存结果
        self.quest_info_cache[quest_id] = quest_info
        return quest_info
    
    def get_comprehensive_chapter_info(self, quest_id: int) -> Dict[str, str]:
        """获取全面的章节信息"""
        chapter_info = {
            'chapter_title': '',
            'chapter_desc': ''
        }
        
        # 根据QuestId模式推断章节
        chapter_id = self.infer_chapter_id(quest_id)
        if chapter_id:
            chapter_info = self.get_chapter_by_id(chapter_id)
            self.stats['chapter_info_found'] += 1
        
        return chapter_info
    
    def infer_chapter_id(self, quest_id: int) -> Optional[int]:
        """根据QuestId推断ChapterId"""
        # 基于分析的模式
        if quest_id >= 139000000 and quest_id < 140000000:
            return 1  # 世界之初
        elif quest_id >= 135000000 and quest_id < 136000000:
            return 2  # 瑝珑第一章
        elif quest_id >= 140000000 and quest_id < 141000000:
            return 3  # 其他章节
        elif quest_id >= 114000000 and quest_id < 115000000:
            return 2  # 瑝珑第一章（吟霖线等）
        else:
            return None
    
    def get_chapter_by_id(self, chapter_id: int) -> Dict[str, str]:
        """根据ChapterId获取章节信息"""
        if chapter_id in self.chapter_info_cache:
            return self.chapter_info_cache[chapter_id]
        
        chapter_info = {
            'chapter_title': '',
            'chapter_desc': ''
        }
        
        # 查找章节信息
        chapter_num_key = f"QuestChapter_{chapter_id}_ChapterNum"
        section_num_key = f"QuestChapter_{chapter_id}_SectionNum"
        chapter_name_key = f"QuestChapter_{chapter_id}_ChapterName"
        
        if chapter_num_key in self.textmap_data:
            chapter_info['chapter_title'] = self.textmap_data[chapter_num_key]
        
        if section_num_key in self.textmap_data:
            chapter_info['section_title'] = self.textmap_data[section_num_key]
        
        if chapter_name_key in self.textmap_data:
            chapter_info['chapter_desc'] = self.textmap_data[chapter_name_key]
        
        # 缓存结果
        self.chapter_info_cache[chapter_id] = chapter_info
        return chapter_info
    
    def get_ecological_info(self, flow_name: str) -> Dict[str, str]:
        """获取生态NPC对话的分类信息"""
        for category, info in self.ecological_categories.items():
            if category in flow_name:
                self.stats['ecological_mapped'] += 1
                return {
                    'chapter_title': info['chapter'],
                    'chapter_desc': '但觉今州胜旧州',
                    'section_title': info['section'],
                    'section_desc': f'{category}区域NPC对话'
                }
        
        return {
            'chapter_title': '',
            'chapter_desc': '',
            'section_title': '',
            'section_desc': ''
        }
    
    def get_character_info(self, flow_name: str) -> Dict[str, str]:
        """获取角色任务对话的分类信息"""
        for character, info in self.character_categories.items():
            if character in flow_name:
                self.stats['character_mapped'] += 1
                return {
                    'chapter_title': info['chapter'],
                    'chapter_desc': '但觉今州胜旧州',
                    'section_title': info['section'],
                    'section_desc': f'{character}角色专属任务对话'
                }
        
        return {
            'chapter_title': '',
            'chapter_desc': '',
            'section_title': '',
            'section_desc': ''
        }
    
    def get_side_quest_info(self, flow_name: str) -> Dict[str, str]:
        """获取支线任务的分类信息"""
        for quest, info in self.side_quest_categories.items():
            if quest in flow_name:
                self.stats['side_quest_mapped'] += 1
                return {
                    'chapter_title': info['chapter'],
                    'chapter_desc': '但觉今州胜旧州',
                    'section_title': info['section'],
                    'section_desc': f'{quest}支线任务对话'
                }
        
        return {
            'chapter_title': '',
            'chapter_desc': '',
            'section_title': '',
            'section_desc': ''
        }
    
    def get_special_info(self, flow_name: str) -> Dict[str, str]:
        """获取特殊类型对话的分类信息"""
        for category, info in self.special_categories.items():
            if category in flow_name:
                self.stats['special_mapped'] += 1
                return {
                    'chapter_title': info['chapter'],
                    'chapter_desc': '特殊内容',
                    'section_title': info['section'],
                    'section_desc': f'{category}相关对话'
                }
        
        return {
            'chapter_title': '',
            'chapter_desc': '',
            'section_title': '',
            'section_desc': ''
        }
    
    def get_smart_section_desc(self, flow_name: str, flow_id: str, state_id: str, quest_id: int, dialogue_text: str) -> str:
        """智能获取section_desc"""
        # 1. 首先检查对话内容模式匹配
        for pattern_info in self.dialogue_content_patterns:
            if re.search(pattern_info['pattern'], dialogue_text):
                self.stats['content_mapping_found'] += 1
                return pattern_info['description']
        
        # 2. 尝试精确的FlowId+StateId映射
        key = f"{flow_name}_{flow_id}_{state_id}"
        if key in self.flow_state_to_tip_mapping:
            self.stats['exact_flow_state_mapping'] += 1
            
            # 查找对应的ChildQuestTip
            mapping_info = self.flow_state_to_tip_mapping[key]
            quest_id_from_mapping = mapping_info['quest_id']
            
            # 在QuestNodeData中查找对应的TidTip
            for item in self.quest_node_data:
                item_key = item.get("Key", "")
                data_str = item.get("Data", "")
                
                try:
                    item_quest_id = int(item_key.split("_")[0])
                    if item_quest_id == quest_id_from_mapping:
                        data_obj = json.loads(data_str)
                        
                        # 检查是否匹配FlowId和StateId
                        if "Condition" in data_obj:
                            condition = data_obj["Condition"]
                            if "Flow" in condition:
                                flow_info = condition["Flow"]
                                if (flow_info.get("FlowListName") == flow_name and 
                                    str(flow_info.get("FlowId")) == flow_id and 
                                    str(flow_info.get("StateId")) == state_id):
                                    
                                    tid_tip = data_obj.get("TidTip", "")
                                    if tid_tip and tid_tip in self.textmap_data:
                                        self.stats['child_tip_found'] += 1
                                        return self.textmap_data[tid_tip]
                        
                        # 检查AddOptions中的Flow
                        if "Condition" in data_obj and "AddOptions" in data_obj["Condition"]:
                            for option in data_obj["Condition"]["AddOptions"]:
                                if "Option" in option and "Type" in option["Option"]:
                                    option_type = option["Option"]["Type"]
                                    if "Flow" in option_type:
                                        flow_info = option_type["Flow"]
                                        if (flow_info.get("FlowListName") == flow_name and 
                                            str(flow_info.get("FlowId")) == flow_id and 
                                            str(flow_info.get("StateId")) == state_id):
                                            
                                            tid_tip = data_obj.get("TidTip", "")
                                            if tid_tip and tid_tip in self.textmap_data:
                                                self.stats['child_tip_found'] += 1
                                                return self.textmap_data[tid_tip]
                                    
                except (json.JSONDecodeError, ValueError):
                    continue
        
        # 3. 回退到原来的方法
        return self.get_fallback_child_tip(quest_id, state_id)
    
    def get_fallback_child_tip(self, quest_id: int, state_id: str) -> str:
        """回退的子任务提示查找方法"""
        if quest_id is None:
            return ""
        
        # 尝试多种ChildQuestTip格式
        possible_patterns = [
            f"Quest_{quest_id}_ChildQuestTip_0_{state_id}",
            f"Quest_{quest_id}_ChildQuestTip_{state_id}_1",
            f"Quest_{quest_id}_ChildQuestTip_311_{state_id}",
            f"Quest_{quest_id}_ChildQuestTip_886_{state_id}",
        ]
        
        for pattern in possible_patterns:
            if pattern in self.textmap_data:
                self.stats['child_tip_found'] += 1
                return self.textmap_data[pattern]
        
        # 模糊匹配
        child_tip_keys = [k for k in self.textmap_data.keys() 
                         if k.startswith(f"Quest_{quest_id}_ChildQuestTip_")]
        
        for key in child_tip_keys:
            if f"_{state_id}" in key or f"{state_id}_" in key:
                self.stats['child_tip_found'] += 1
                return self.textmap_data[key]
        
        return ""
    
    def parse_dialogue_doc_id(self, doc_id: str) -> Dict[str, str]:
        """正确解析对话doc_id"""
        if not doc_id.startswith("dialogue_"):
            return {}
        
        # 移除 "dialogue_" 前缀
        remaining = doc_id[9:]
        parts = remaining.split('_')
        
        if len(parts) >= 4:
            # 重新组合flow_name
            flow_name_parts = parts[:-3]
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
                    
                    # 解析doc_id
                    doc_info = self.parse_dialogue_doc_id(doc_id)
                    if not doc_info:
                        continue
                    
                    flow_name = doc_info['flow_name']
                    quest_id = self.flow_to_quest_mapping.get(flow_name)
                    
                    if quest_id:
                        mapped_count += 1
                        quest_info = self.get_comprehensive_quest_info(quest_id)
                        
                        # 使用智能的section_desc查找
                        section_desc = self.get_smart_section_desc(
                            flow_name, 
                            doc_info['flow_id'], 
                            doc_info['state_id'], 
                            quest_id,
                            text
                        )
                        
                        # 构建最终数据
                        final_item = {
                            'doc_id': doc_id,
                            'quest_id': quest_id,
                            'quest_name': quest_info['quest_name'],
                            'quest_desc': quest_info['quest_desc'],
                            'chapter_title': quest_info['chapter_title'],
                            'chapter_desc': quest_info['chapter_desc'],
                            'section_title': quest_info['section_title'],
                            'section_desc': section_desc,
                            'flow_id': doc_info['flow_id'],
                            'state_id': doc_info['state_id'],
                            'dialogue_id': doc_info['dialogue_id'],
                            'text': text
                        }
                    else:
                        # 未映射的情况 - 尝试各种分类
                        ecological_info = self.get_ecological_info(flow_name)
                        character_info = self.get_character_info(flow_name)
                        side_quest_info = self.get_side_quest_info(flow_name)
                        special_info = self.get_special_info(flow_name)
                        
                        if ecological_info['chapter_title']:
                            # 生态NPC对话
                            final_item = {
                                'doc_id': doc_id,
                                'quest_id': None,
                                'quest_name': '生态NPC对话',
                                'quest_desc': f'{flow_name}区域的环境对话',
                                'chapter_title': ecological_info['chapter_title'],
                                'chapter_desc': ecological_info['chapter_desc'],
                                'section_title': ecological_info['section_title'],
                                'section_desc': ecological_info['section_desc'],
                                'flow_id': doc_info['flow_id'],
                                'state_id': doc_info['state_id'],
                                'dialogue_id': doc_info['dialogue_id'],
                                'text': text
                            }
                        elif character_info['chapter_title']:
                            # 角色任务对话
                            final_item = {
                                'doc_id': doc_id,
                                'quest_id': None,
                                'quest_name': '角色任务对话',
                                'quest_desc': f'{flow_name}角色专属任务对话',
                                'chapter_title': character_info['chapter_title'],
                                'chapter_desc': character_info['chapter_desc'],
                                'section_title': character_info['section_title'],
                                'section_desc': character_info['section_desc'],
                                'flow_id': doc_info['flow_id'],
                                'state_id': doc_info['state_id'],
                                'dialogue_id': doc_info['dialogue_id'],
                                'text': text
                            }
                        elif side_quest_info['chapter_title']:
                            # 支线任务对话
                            final_item = {
                                'doc_id': doc_id,
                                'quest_id': None,
                                'quest_name': '支线任务对话',
                                'quest_desc': f'{flow_name}支线任务对话',
                                'chapter_title': side_quest_info['chapter_title'],
                                'chapter_desc': side_quest_info['chapter_desc'],
                                'section_title': side_quest_info['section_title'],
                                'section_desc': side_quest_info['section_desc'],
                                'flow_id': doc_info['flow_id'],
                                'state_id': doc_info['state_id'],
                                'dialogue_id': doc_info['dialogue_id'],
                                'text': text
                            }
                        elif special_info['chapter_title']:
                            # 特殊类型对话
                            final_item = {
                                'doc_id': doc_id,
                                'quest_id': None,
                                'quest_name': '特殊对话',
                                'quest_desc': f'{flow_name}特殊内容对话',
                                'chapter_title': special_info['chapter_title'],
                                'chapter_desc': special_info['chapter_desc'],
                                'section_title': special_info['section_title'],
                                'section_desc': special_info['section_desc'],
                                'flow_id': doc_info['flow_id'],
                                'state_id': doc_info['state_id'],
                                'dialogue_id': doc_info['dialogue_id'],
                                'text': text
                            }
                        else:
                            # 完全未映射的情况
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
        
        # 更新统计
        self.stats['total_dialogues'] = processed_count
        self.stats['mapped_dialogues'] = mapped_count
        
        print(f"Processing complete!")
        print(f"Total processed: {processed_count}")
        print(f"Successfully mapped: {mapped_count}")
        print(f"Mapping rate: {mapped_count/processed_count*100:.1f}%")
    
    def print_final_statistics(self):
        """打印最终统计信息"""
        print("\n" + "="*60)
        print("ULTIMATE PROCESSING STATISTICS")
        print("="*60)
        print(f"Total dialogues processed: {self.stats['total_dialogues']}")
        print(f"Successfully mapped: {self.stats['mapped_dialogues']}")
        print(f"Mapping rate: {self.stats['mapped_dialogues']/self.stats['total_dialogues']*100:.1f}%")
        print(f"Quest names found: {self.stats['quest_name_found']}")
        print(f"Quest descriptions found: {self.stats['quest_desc_found']}")
        print(f"Chapter info found: {self.stats['chapter_info_found']}")
        print(f"Child tips found: {self.stats['child_tip_found']}")
        print(f"Exact flow+state mappings: {self.stats['exact_flow_state_mapping']}")
        print(f"Content mappings found: {self.stats['content_mapping_found']}")
        print(f"Ecological mappings found: {self.stats['ecological_mapped']}")
        print(f"Character mappings found: {self.stats['character_mapped']}")
        print(f"Side quest mappings found: {self.stats['side_quest_mapped']}")
        print(f"Special mappings found: {self.stats['special_mapped']}")
        
        # 计算质量指标
        if self.stats['total_dialogues'] > 0:
            quest_name_rate = self.stats['quest_name_found'] / self.stats['total_dialogues'] * 100
            quest_desc_rate = self.stats['quest_desc_found'] / self.stats['total_dialogues'] * 100
            chapter_rate = (self.stats['chapter_info_found'] + self.stats['ecological_mapped'] + 
                          self.stats['character_mapped'] + self.stats['side_quest_mapped'] + 
                          self.stats['special_mapped']) / self.stats['total_dialogues'] * 100
            child_tip_rate = self.stats['child_tip_found'] / self.stats['total_dialogues'] * 100
            
            print(f"\nQuality metrics (for all dialogues):")
            print(f"Quest name coverage: {quest_name_rate:.1f}%")
            print(f"Quest description coverage: {quest_desc_rate:.1f}%")
            print(f"Chapter info coverage: {chapter_rate:.1f}%")
            print(f"Child tip coverage: {child_tip_rate:.1f}%")
    
    def run(self):
        """运行完整的处理流程"""
        print("=== ULTIMATE DIALOGUE PROCESSOR ===")
        print("Fixes all mapping issues including side quests and character dialogues")
        
        # 1. 加载配置
        self.load_configurations()
        
        # 2. 建立映射
        self.build_comprehensive_mapping()
        
        # 3. 处理数据
        input_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
        output_file = "WutheringDialog/data/dialogs_zh-Hans.ultimate_complete.jsonl"
        
        self.process_dialogue_data(input_file, output_file)
        
        # 4. 打印统计
        self.print_final_statistics()
        
        print(f"\nUltimate complete dataset saved to: {output_file}")

if __name__ == "__main__":
    processor = UltimateDialogueProcessor()
    processor.run()
