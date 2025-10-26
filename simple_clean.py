#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import os

def clean_dialogue_data():
    print("=== 开始清洗对话数据 ===")
    
    # 加载TextMap
    print("加载TextMap...")
    with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
        textmap = json.load(f)
    print(f"TextMap加载完成，共 {len(textmap)} 条记录")
    
    # 读取对话文件
    print("读取对话文件...")
    with open("WutheringDialog/data/dialogs_zh-Hans.split.jsonl", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"对话文件读取完成，共 {len(lines)} 行")
    
    # 处理每一行
    cleaned_data = []
    
    for i, line in enumerate(lines):
        if i % 1000 == 0:
            print(f"处理进度: {i}/{len(lines)}")
            
        try:
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', '')
            text = data.get('text', '')
            
            # 解析doc_id: dialogue_剧情_新剧本测试_1_1_0
            parts = doc_id.split('_')
            if len(parts) >= 6:
                quest_type = parts[1]  # 剧情
                quest_name = parts[2]  # 新剧本测试
                quest_id = parts[3]    # 1
                section_id = parts[4]   # 1
                dialogue_id = parts[5]  # 0
                
                # 构建新的数据结构
                cleaned_item = {
                    'doc_id': doc_id,
                    'quest_type': quest_type,
                    'quest_name': quest_name,
                    'quest_id': quest_id,
                    'section_id': section_id,
                    'dialogue_id': dialogue_id,
                    'text': text,
                    'chapter_title': '',
                    'chapter_desc': '',
                    'section_title': '',
                    'section_desc': '',
                    'quest_desc': '',
                    'child_tip': ''
                }
                
                # 尝试从TextMap中获取更多信息
                # 查找章节信息
                for key, value in textmap.items():
                    if key.startswith(f"QuestChapter_{quest_id}_"):
                        if "ChapterName" in key:
                            cleaned_item['chapter_title'] = value
                        elif "ChapterNum" in key:
                            cleaned_item['section_title'] = value
                        elif "SectionNum" in key:
                            cleaned_item['section_desc'] = value
                
                # 查找任务描述
                quest_desc_key = f"Quest_{quest_id}000025_QuestDesc_0_2"
                if quest_desc_key in textmap:
                    cleaned_item['quest_desc'] = textmap[quest_desc_key]
                
                # 查找子任务提示
                child_tip_key = f"Quest_{quest_id}000025_ChildQuestTip_0_{dialogue_id}"
                if child_tip_key in textmap:
                    cleaned_item['child_tip'] = textmap[child_tip_key]
                
                cleaned_data.append(cleaned_item)
            
        except json.JSONDecodeError as e:
            print(f"第 {i+1} 行JSON解析错误: {e}")
            continue
    
    # 保存清洗后的数据
    output_file = "WutheringDialog/data/dialogs_zh-Hans.cleaned.jsonl"
    print(f"\n保存清洗后的数据到 {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in cleaned_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"清洗完成！共处理了 {len(cleaned_data)} 条记录")
    
    # 显示几个示例
    print("\n=== 清洗后的数据示例 ===")
    for i, item in enumerate(cleaned_data[:3]):
        print(f"\n示例 {i+1}:")
        print(f"  doc_id: {item['doc_id']}")
        print(f"  chapter_title: {item['chapter_title']}")
        print(f"  section_title: {item['section_title']}")
        print(f"  quest_desc: {item['quest_desc']}")
        print(f"  child_tip: {item['child_tip']}")
        print(f"  text: {item['text'][:100]}...")

if __name__ == "__main__":
    clean_dialogue_data()

