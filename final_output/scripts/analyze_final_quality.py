#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from collections import defaultdict, Counter

def analyze_final_quality():
    """分析最终数据质量"""
    
    dialogue_file = "WutheringDialog/data/dialogs_zh-Hans.complete_final.jsonl"
    
    print("=== 最终数据质量分析 ===")
    
    total_records = 0
    quest_id_stats = Counter()
    quest_name_stats = Counter()
    chapter_title_stats = Counter()
    section_title_stats = Counter()
    section_desc_stats = Counter()
    
    # 分类统计
    ecological_count = 0
    character_count = 0
    main_story_count = 0
    side_quest_count = 0
    special_count = 0
    unknown_count = 0
    
    # 质量统计
    quest_name_filled = 0
    quest_desc_filled = 0
    chapter_title_filled = 0
    chapter_desc_filled = 0
    section_title_filled = 0
    section_desc_filled = 0
    
    with open(dialogue_file, 'r', encoding='utf-8') as f:
        for line in f:
            total_records += 1
            data = json.loads(line.strip())
            
            # 统计quest_id
            quest_id = data.get('quest_id')
            if quest_id is not None:
                quest_id_stats['mapped'] += 1
            else:
                quest_id_stats['null'] += 1
            
            # 统计quest_name
            quest_name = data.get('quest_name', '')
            quest_name_stats[quest_name] += 1
            if quest_name and quest_name != 'Unknown':
                quest_name_filled += 1
            
            # 统计quest_desc
            quest_desc = data.get('quest_desc', '')
            if quest_desc and quest_desc != 'Unknown':
                quest_desc_filled += 1
            
            # 统计chapter_title
            chapter_title = data.get('chapter_title', '')
            chapter_title_stats[chapter_title] += 1
            if chapter_title and chapter_title != 'Unknown':
                chapter_title_filled += 1
            
            # 统计chapter_desc
            chapter_desc = data.get('chapter_desc', '')
            if chapter_desc and chapter_desc != 'Unknown':
                chapter_desc_filled += 1
            
            # 统计section_title
            section_title = data.get('section_title', '')
            section_title_stats[section_title] += 1
            if section_title and section_title != 'Unknown':
                section_title_filled += 1
            
            # 统计section_desc
            section_desc = data.get('section_desc', '')
            section_desc_stats[section_desc] += 1
            if section_desc and section_desc != 'Unknown':
                section_desc_filled += 1
            
            # 分类统计
            if quest_name == '生态NPC对话':
                ecological_count += 1
            elif quest_name == '角色任务对话':
                character_count += 1
            elif quest_name == '主线剧情对话':
                main_story_count += 1
            elif quest_name == '支线任务对话':
                side_quest_count += 1
            elif quest_name == '特殊对话':
                special_count += 1
            elif quest_name == 'Unknown':
                unknown_count += 1
    
    print(f"总记录数: {total_records}")
    print(f"\n=== Quest ID 映射统计 ===")
    print(f"成功映射: {quest_id_stats['mapped']} ({quest_id_stats['mapped']/total_records*100:.1f}%)")
    print(f"未映射: {quest_id_stats['null']} ({quest_id_stats['null']/total_records*100:.1f}%)")
    
    print(f"\n=== 字段填充统计 ===")
    print(f"Quest Name 填充: {quest_name_filled} ({quest_name_filled/total_records*100:.1f}%)")
    print(f"Quest Desc 填充: {quest_desc_filled} ({quest_desc_filled/total_records*100:.1f}%)")
    print(f"Chapter Title 填充: {chapter_title_filled} ({chapter_title_filled/total_records*100:.1f}%)")
    print(f"Chapter Desc 填充: {chapter_desc_filled} ({chapter_desc_filled/total_records*100:.1f}%)")
    print(f"Section Title 填充: {section_title_filled} ({section_title_filled/total_records*100:.1f}%)")
    print(f"Section Desc 填充: {section_desc_filled} ({section_desc_filled/total_records*100:.1f}%)")
    
    print(f"\n=== 分类统计 ===")
    print(f"生态NPC对话: {ecological_count} ({ecological_count/total_records*100:.1f}%)")
    print(f"角色任务对话: {character_count} ({character_count/total_records*100:.1f}%)")
    print(f"主线剧情对话: {main_story_count} ({main_story_count/total_records*100:.1f}%)")
    print(f"支线任务对话: {side_quest_count} ({side_quest_count/total_records*100:.1f}%)")
    print(f"特殊对话: {special_count} ({special_count/total_records*100:.1f}%)")
    print(f"Unknown: {unknown_count} ({unknown_count/total_records*100:.1f}%)")
    
    print(f"\n=== Top 10 Quest Names ===")
    for quest_name, count in quest_name_stats.most_common(10):
        print(f"  {quest_name}: {count} ({count/total_records*100:.1f}%)")
    
    print(f"\n=== Top 10 Chapter Titles ===")
    for chapter_title, count in chapter_title_stats.most_common(10):
        print(f"  {chapter_title}: {count} ({count/total_records*100:.1f}%)")
    
    print(f"\n=== Top 10 Section Titles ===")
    for section_title, count in section_title_stats.most_common(10):
        print(f"  {section_title}: {count} ({count/total_records*100:.1f}%)")

if __name__ == "__main__":
    analyze_final_quality()
