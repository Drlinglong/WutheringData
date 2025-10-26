#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import os
from typing import Dict, List, Tuple, Optional

class DialogueDataCleaner:
    def __init__(self, textmap_path: str, dialogue_file: str):
        self.textmap_path = textmap_path
        self.dialogue_file = dialogue_file
        self.textmap_data = {}
        self.quest_mapping = {}
        
    def load_textmap(self):
        """加载TextMap数据"""
        print("加载TextMap数据...")
        with open(self.textmap_path, 'r', encoding='utf-8') as f:
            self.textmap_data = json.load(f)
        print(f"加载了 {len(self.textmap_data)} 条TextMap记录")
        
    def build_quest_mapping(self):
        """构建任务映射表"""
        print("构建任务映射表...")
        
        # 提取章节信息
        chapters = {}
        sections = {}
        
        for key, value in self.textmap_data.items():
            if key.startswith("QuestChapter_"):
                parts = key.split("_")
                if len(parts) >= 4:
                    chapter_id = parts[1]
                    field = parts[3]
                    
                    if chapter_id not in chapters:
                        chapters[chapter_id] = {}
                    chapters[chapter_id][field] = value
                    
            elif key.startswith("Quest_") and "_QuestDesc_" in key:
                # 提取任务描述
                match = re.match(r"Quest_(\d+)_QuestDesc_(\d+)_(\d+)", key)
                if match:
                    quest_id = match.group(1)
                    if quest_id not in self.quest_mapping:
                        self.quest_mapping[quest_id] = {}
                    self.quest_mapping[quest_id]['desc'] = value
                    
            elif key.startswith("Quest_") and "_QuestName_" in key:
                # 提取任务名称
                match = re.match(r"Quest_(\d+)_QuestName_(\d+)_(\d+)", key)
                if match:
                    quest_id = match.group(1)
                    if quest_id not in self.quest_mapping:
                        self.quest_mapping[quest_id] = {}
                    self.quest_mapping[quest_id]['name'] = value
                    
            elif key.startswith("Quest_") and "_ChildQuestTip_" in key:
                # 提取子任务提示
                match = re.match(r"Quest_(\d+)_ChildQuestTip_(\d+)_(\d+)", key)
                if match:
                    quest_id = match.group(1)
                    child_id = match.group(3)
                    if quest_id not in self.quest_mapping:
                        self.quest_mapping[quest_id] = {}
                    if 'child_tips' not in self.quest_mapping[quest_id]:
                        self.quest_mapping[quest_id]['child_tips'] = {}
                    self.quest_mapping[quest_id]['child_tips'][child_id] = value
        
        print(f"构建了 {len(self.quest_mapping)} 个任务映射")
        
    def parse_dialogue_id(self, doc_id: str) -> Dict[str, str]:
        """解析对话ID，提取任务信息"""
        # 格式: dialogue_剧情_新剧本测试_1_1_0
        parts = doc_id.split("_")
        if len(parts) < 6:
            return {}
            
        quest_type = parts[1]  # 剧情
        quest_name = parts[2]  # 新剧本测试
        quest_id = parts[3]    # 1
        section_id = parts[4]   # 1
        dialogue_id = parts[5]  # 0
        
        return {
            'quest_type': quest_type,
            'quest_name': quest_name,
            'quest_id': quest_id,
            'section_id': section_id,
            'dialogue_id': dialogue_id
        }
    
    def get_quest_context(self, quest_info: Dict[str, str]) -> Dict[str, str]:
        """获取任务上下文信息"""
        context = {
            'chapter_title': '',
            'chapter_desc': '',
            'section_title': '',
            'section_desc': '',
            'quest_name': '',
            'quest_desc': '',
            'child_tip': ''
        }
        
        quest_id = quest_info.get('quest_id', '')
        section_id = quest_info.get('section_id', '')
        dialogue_id = quest_info.get('dialogue_id', '')
        
        # 获取任务信息
        if quest_id in self.quest_mapping:
            quest_data = self.quest_mapping[quest_id]
            context['quest_name'] = quest_data.get('name', '')
            context['quest_desc'] = quest_data.get('desc', '')
            
            # 获取子任务提示
            child_tips = quest_data.get('child_tips', {})
            if dialogue_id in child_tips:
                context['child_tip'] = child_tips[dialogue_id]
        
        # 获取章节信息（需要根据quest_id映射到章节）
        # 这里需要根据实际的数据结构来完善
        for key, value in self.textmap_data.items():
            if key.startswith("QuestChapter_"):
                parts = key.split("_")
                if len(parts) >= 4:
                    chapter_id = parts[1]
                    field = parts[3]
                    
                    # 简单的映射逻辑，可能需要根据实际情况调整
                    if chapter_id == quest_id:
                        if field == "ChapterName":
                            context['chapter_title'] = value
                        elif field == "ChapterNum":
                            context['section_title'] = value
                        elif field == "SectionNum":
                            context['section_desc'] = value
        
        return context
    
    def clean_dialogue_data(self, output_file: str):
        """清洗对话数据"""
        print("开始清洗对话数据...")
        
        cleaned_data = []
        
        with open(self.dialogue_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num % 1000 == 0:
                    print(f"处理了 {line_num} 行...")
                    
                try:
                    data = json.loads(line.strip())
                    doc_id = data.get('doc_id', '')
                    text = data.get('text', '')
                    
                    # 解析对话ID
                    quest_info = self.parse_dialogue_id(doc_id)
                    if not quest_info:
                        continue
                    
                    # 获取上下文信息
                    context = self.get_quest_context(quest_info)
                    
                    # 构建新的数据结构
                    cleaned_item = {
                        'doc_id': doc_id,
                        'chapter_title': context['chapter_title'],
                        'chapter_desc': context['chapter_desc'],
                        'section_title': context['section_title'],
                        'section_desc': context['section_desc'],
                        'quest_name': context['quest_name'],
                        'quest_desc': context['quest_desc'],
                        'child_tip': context['child_tip'],
                        'text': text
                    }
                    
                    cleaned_data.append(cleaned_item)
                    
                except json.JSONDecodeError as e:
                    print(f"第 {line_num} 行JSON解析错误: {e}")
                    continue
        
        # 保存清洗后的数据
        print(f"保存清洗后的数据到 {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in cleaned_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"清洗完成！共处理了 {len(cleaned_data)} 条记录")
        return len(cleaned_data)

def main():
    # 文件路径
    textmap_file = "TextMap/zh-Hans/MultiText.json"
    dialogue_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
    output_file = "WutheringDialog/data/dialogs_zh-Hans.cleaned.jsonl"
    
    # 检查文件是否存在
    if not os.path.exists(textmap_file):
        print(f"TextMap文件不存在: {textmap_file}")
        return
        
    if not os.path.exists(dialogue_file):
        print(f"对话文件不存在: {dialogue_file}")
        return
    
    # 创建清洗器
    cleaner = DialogueDataCleaner(textmap_file, dialogue_file)
    
    # 加载数据
    cleaner.load_textmap()
    cleaner.build_quest_mapping()
    
    # 清洗数据
    count = cleaner.clean_dialogue_data(output_file)
    
    print(f"\n数据清洗完成！")
    print(f"输出文件: {output_file}")
    print(f"处理记录数: {count}")

if __name__ == "__main__":
    main()

