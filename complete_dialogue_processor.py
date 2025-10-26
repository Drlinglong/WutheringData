#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

class CompleteDialogueProcessor:
    """
    完整版对话处理器 - 修复所有映射问题包括所有生态区域
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
        
        # 全面的生态NPC对话分类（基于自动扫描结果）
        # ⚠️ 为什么需要这么多手动分类？
        # 因为游戏公司的flow_name设计极其混乱，没有任何统一规则
        # 比如："剧情_七丘生态_NPC"、"中曲生态"、"NPC对话" 等等都是不同的命名风格
        # 无法通过任何算法自动匹配，只能手动枚举
        # 未来如有新的flow_name，运行 auto_scan_categories.py 扫描后手动添加
        self.ecological_categories = {
            # 瑝珑第二章生态对话
            '剧情_七丘生态_NPC': {'chapter': '瑝珑 第二章', 'section': '七丘生态对话'},
            '剧情_1_1_乘宵山生态_NPC_配音': {'chapter': '瑝珑 第二章', 'section': '乘宵山生态对话'},
            '剧情_2_4_巴别塔演出_上1': {'chapter': '瑝珑 第二章', 'section': '巴别塔演出对话'},
            '剧情_中曲台_NPC对话和冒泡': {'chapter': '瑝珑 第二章', 'section': '中曲台生态对话'},
            '剧情_2_4_巴别塔演出_上2': {'chapter': '瑝珑 第二章', 'section': '巴别塔演出对话'},
            '剧情_2_4_巴别塔演出_下': {'chapter': '瑝珑 第二章', 'section': '巴别塔演出对话'},
            '剧情_2_4_活动_要塞生态': {'chapter': '瑝珑 第二章', 'section': '要塞生态对话'},
            '剧情_2_5_巴别塔演出_下篇': {'chapter': '瑝珑 第二章', 'section': '巴别塔演出对话'},
            '剧情_2_7支线_重建桑古伊斯水城': {'chapter': '瑝珑 第二章', 'section': '重建水城生态'},
            '剧情_七丘_浴场生态': {'chapter': '瑝珑 第二章', 'section': '浴场生态对话'},
            '剧情_七丘_要塞生态': {'chapter': '瑝珑 第二章', 'section': '要塞生态对话'},
            '剧情_2_7生态替换JXY': {'chapter': '瑝珑 第二章', 'section': '生态替换对话'},
            '剧情_七丘生态_NPC_研究院': {'chapter': '瑝珑 第二章', 'section': '研究院生态对话'},
            '剧情_V1.2版本更新生态对话': {'chapter': '瑝珑 第二章', 'section': '版本更新生态'},
            '剧情_七丘要塞生态2_0': {'chapter': '瑝珑 第二章', 'section': '七丘要塞生态'},
            '剧情_七丘_列奥尼达广场生态': {'chapter': '瑝珑 第二章', 'section': '列奥尼达广场生态'},
            '剧情_七丘_列奥尼达广场生态': {'chapter': '瑝珑 第二章', 'section': '列奥尼达广场生态'},
            '剧情_桑原_建设狮鹫营地': {'chapter': '瑝珑 第二章', 'section': '狮鹫营地生态'},
            '剧情_旧贵族宅邸_人文生态对话和冒泡': {'chapter': '瑝珑 第二章', 'section': '旧贵族宅邸生态'},
            '剧情_中曲台地建设狮鹫营地POI': {'chapter': '瑝珑 第二章', 'section': '中曲台地生态'},
            
            # 瑝珑第一章生态对话
            '中曲生态': {'chapter': '瑝珑 第一章', 'section': '中曲台地生态'},
            '虎口生态': {'chapter': '瑝珑 第一章', 'section': '虎口矿场生态'},
            '荒石生态': {'chapter': '瑝珑 第一章', 'section': '荒石高地生态'},
            '天城生态': {'chapter': '瑝珑 第一章', 'section': '今州城生态'},
            '北落野生态': {'chapter': '瑝珑 第一章', 'section': '北落野生态'},
            '乘宵山': {'chapter': '瑝珑 第一章', 'section': '乘宵山虹镇生态'},
            '金库下层': {'chapter': '瑝珑 第一章', 'section': '金库下层生态'},
            '旧贵族宅邸': {'chapter': '瑝珑 第一章', 'section': '旧贵族宅邸生态'},
            '人文生态': {'chapter': '瑝珑 第一章', 'section': '人文生态对话'},
            'NPC对话': {'chapter': '瑝珑 第一章', 'section': 'NPC生态对话'},
            '生态对话': {'chapter': '瑝珑 第一章', 'section': '生态对话'},
            '生态冒泡': {'chapter': '瑝珑 第一章', 'section': '生态冒泡对话'},
            '回魂夜氛围': {'chapter': '瑝珑 第一章', 'section': '回魂夜氛围对话'},
            '氛围NPC': {'chapter': '瑝珑 第一章', 'section': '氛围NPC对话'},
            'NPC冒泡': {'chapter': '瑝珑 第一章', 'section': 'NPC冒泡对话'},
            '配音生态': {'chapter': '瑝珑 第一章', 'section': '配音生态对话'},
            '配音生态冒泡': {'chapter': '瑝珑 第一章', 'section': '配音生态冒泡'},
        }
        
        # 角色任务对话的分类（基于自动扫描结果）
        # 同上，也是手动枚举的无奈之举
        self.character_categories = {
            # 瑝珑第二章角色线
            '剧情_2_2_维奥拉角色线': {'chapter': '瑝珑 第二章', 'section': '维奥拉角色线'},
            '剧情_1_3_吟霖角色线': {'chapter': '瑝珑 第二章', 'section': '吟霖角色线'},
            '剧情_2_7_狄斯台地主线_上半_巡游者': {'chapter': '瑝珑 第二章', 'section': '巡游者角色线'},
            '剧情_1_2_角色_寸草心': {'chapter': '瑝珑 第二章', 'section': '寸草心角色线'},
            '剧情_角色_吟霖线新': {'chapter': '瑝珑 第二章', 'section': '吟霖线新角色线'},
            '剧情_1_1_乘宵山角色线': {'chapter': '瑝珑 第二章', 'section': '乘宵山角色线'},
            '剧情_2_0_角色_吟霖线新': {'chapter': '瑝珑 第二章', 'section': '吟霖线新角色线'},
            '剧情_2_7_桑古伊斯水城_上半_1': {'chapter': '瑝珑 第二章', 'section': '桑古伊斯水城角色线'},
            '剧情_吟霖_吟霖线1': {'chapter': '瑝珑 第二章', 'section': '吟霖线角色线'},
            '剧情_1_3_角色_吟霖线新': {'chapter': '瑝珑 第二章', 'section': '吟霖线新角色线'},
            '剧情_V1.2版本更新角色线': {'chapter': '瑝珑 第二章', 'section': '版本更新角色线'},
            '剧情_七丘_角色_吟霖线新': {'chapter': '瑝珑 第二章', 'section': '吟霖线新角色线'},
            '剧情_吟霖_吟霖线': {'chapter': '瑝珑 第二章', 'section': '吟霖线角色线'},
            '剧情_2_0_桑古伊斯水城_第一幕': {'chapter': '瑝珑 第二章', 'section': '桑古伊斯水城角色线'},
            '剧情_1.2同版本更新支线': {'chapter': '瑝珑 第二章', 'section': '版本更新支线'},
            
            # 瑝珑第一章角色线
            '余果': {'chapter': '瑝珑 第一章', 'section': '角色任务对话'},
            '刘梦蝶': {'chapter': '瑝珑 第一章', 'section': '角色任务对话'},
            '寸草心': {'chapter': '瑝珑 第一章', 'section': '角色任务对话'},
            '忌炎线': {'chapter': '瑝珑 第一章', 'section': '忌炎角色线'},
            '吟霖线': {'chapter': '瑝珑 第一章', 'section': '吟霖角色线'},
            '散华线': {'chapter': '瑝珑 第一章', 'section': '散华角色线'},
            '白芷线': {'chapter': '瑝珑 第一章', 'section': '白芷角色线'},
            '赞妮副本': {'chapter': '瑝珑 第一章', 'section': '赞妮角色副本'},
            '夏空线': {'chapter': '瑝珑 第一章', 'section': '夏空角色线'},
            'V2.3': {'chapter': '瑝珑 第一章', 'section': '版本更新角色线'},
        }
        
        # 支线任务的分类
        self.side_quest_categories = {
            '支线': {'chapter': '瑝珑 第一章', 'section': '支线任务'},
            '布偶小队历险记': {'chapter': '瑝珑 第一章', 'section': '布偶小队历险记'},
            '猫猫咖啡厅': {'chapter': '瑝珑 第一章', 'section': '猫猫咖啡厅'},
            '灯塔迷航': {'chapter': '瑝珑 第一章', 'section': '灯塔迷航'},
            '沉没的历史': {'chapter': '瑝珑 第一章', 'section': '沉没的历史'},
            
            # 团团转系列
            '团团团团转': {'chapter': '瑝珑 第一章', 'section': '团团团团转支线'},
            '团团转': {'chapter': '瑝珑 第一章', 'section': '团团转支线'},
            
            # 记忆手册系列
            '团子记忆手册': {'chapter': '瑝珑 第一章', 'section': '团子记忆手册'},
            '记忆手册': {'chapter': '瑝珑 第一章', 'section': '记忆手册任务'},
        }
        
        # 主线剧情分类（基于自动扫描结果）
        self.main_story_categories = {
            # 瑝珑第二章主线剧情
            '剧情_POI_瑝珑台': {'chapter': '瑝珑 第二章', 'section': '瑝珑台主线'},
            '剧情_桑原_一阶POI剧情对话': {'chapter': '瑝珑 第二章', 'section': '桑原主线'},
            '剧情_七丘_乘宵山_剧情对话': {'chapter': '瑝珑 第二章', 'section': '乘宵山主线'},
            '剧情_2_4_活动_瑝珑之战': {'chapter': '瑝珑 第二章', 'section': '瑝珑之战主线'},
            '剧情_2_1_七丘_瑝珑要塞_下篇_POI对话': {'chapter': '瑝珑 第二章', 'section': '瑝珑要塞主线'},
            '剧情_桑原_剧场_瑝珑POI对话': {'chapter': '瑝珑 第二章', 'section': '剧场主线'},
            '剧情_2.4_瑝珑渊碎片': {'chapter': '瑝珑 第二章', 'section': '瑝珑渊主线'},
            '剧情_七丘_瑝珑要塞_无光之森林危机': {'chapter': '瑝珑 第二章', 'section': '无光森林主线'},
            '剧情_七丘_瑝珑台': {'chapter': '瑝珑 第二章', 'section': '瑝珑台主线'},
            '剧情_荒石高地_瑝珑要塞': {'chapter': '瑝珑 第二章', 'section': '荒石高地主线'},
            '剧情_2_0_七丘_瑝珑要塞_POI对话': {'chapter': '瑝珑 第二章', 'section': '瑝珑要塞主线'},
            '剧情_瑝珑要塞旋转': {'chapter': '瑝珑 第二章', 'section': '瑝珑要塞主线'},
            '剧情_2_0_瑝珑台_瑝珑要塞': {'chapter': '瑝珑 第二章', 'section': '瑝珑台主线'},
            '剧情_乘宵山_瑝珑要塞_瑝珑式': {'chapter': '瑝珑 第二章', 'section': '瑝珑式主线'},
            '剧情_活动_V1.0瑝珑活动': {'chapter': '瑝珑 第二章', 'section': '瑝珑活动主线'},
            
            # 巴别塔相关
            '2_6_狄斯台地主线': {'chapter': '瑝珑 第二章', 'section': '狄斯台地主线'},
            '2_4_巴别塔': {'chapter': '瑝珑 第二章', 'section': '巴别塔剧情'},
            '巴别塔演出': {'chapter': '瑝珑 第二章', 'section': '巴别塔演出'},
            '巴别塔领主': {'chapter': '瑝珑 第二章', 'section': '巴别塔领主'},
            '狄斯台地': {'chapter': '瑝珑 第二章', 'section': '狄斯台地剧情'},
            '赤林台地': {'chapter': '瑝珑 第二章', 'section': '赤林台地剧情'},
            '主线': {'chapter': '瑝珑 第二章', 'section': '主线剧情'},
            '剧情': {'chapter': '瑝珑 第二章', 'section': '剧情对话'},
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
            'main_story_mapped': 0,
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
    
    def get_main_story_info(self, flow_name: str) -> Dict[str, str]:
        """获取主线剧情对话的分类信息"""
        for category, info in self.main_story_categories.items():
            if category in flow_name:
                self.stats['main_story_mapped'] += 1
                return {
                    'chapter_title': info['chapter'],
                    'chapter_desc': '瑝珑第二章主线剧情',
                    'section_title': info['section'],
                    'section_desc': f'{category}主线剧情对话'
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
                        main_story_info = self.get_main_story_info(flow_name)
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
                        elif main_story_info['chapter_title']:
                            # 主线剧情对话
                            final_item = {
                                'doc_id': doc_id,
                                'quest_id': None,
                                'quest_name': '主线剧情对话',
                                'quest_desc': f'{flow_name}主线剧情对话',
                                'chapter_title': main_story_info['chapter_title'],
                                'chapter_desc': main_story_info['chapter_desc'],
                                'section_title': main_story_info['section_title'],
                                'section_desc': main_story_info['section_desc'],
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
        print("COMPLETE PROCESSING STATISTICS")
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
        
        
        # ⚠️ 数据结构预警：如果未来游戏更新添加了新的flow_name
        # 1. 运行 auto_scan_categories.py 扫描所有唯一的flow_name
        # 2. 手动将新的flow_name分类到对应的 _categories 字典中
        # 3. 这是一个无奈的设计，因为游戏公司的数据结构没有统一规则
        
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
        print("=== COMPLETE DIALOGUE PROCESSOR ===")
        print("Fixes all mapping issues including all ecological regions")
        
        # 1. 加载配置
        self.load_configurations()
        
        # 2. 建立映射
        self.build_comprehensive_mapping()
        
        # 3. 处理数据
        input_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
        output_file = "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"
        
        self.process_dialogue_data(input_file, output_file)
        
        # 4. 打印统计
        self.print_final_statistics()
        
        print(f"\nComplete final dataset saved to: {output_file}")

if __name__ == "__main__":
    processor = CompleteDialogueProcessor()
    processor.run()
