#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

def clean_dialogue_data():
    print("Starting dialogue data cleaning...")
    
    # Load TextMap
    print("Loading TextMap...")
    with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
        textmap = json.load(f)
    print(f"TextMap loaded: {len(textmap)} records")
    
    # Read dialogue file
    print("Reading dialogue file...")
    with open("WutheringDialog/data/dialogs_zh-Hans.split.jsonl", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Dialogue file read: {len(lines)} lines")
    
    # Process each line
    cleaned_data = []
    
    for i, line in enumerate(lines):
        if i % 5000 == 0:
            print(f"Progress: {i}/{len(lines)}")
            
        try:
            data = json.loads(line.strip())
            doc_id = data.get('doc_id', '')
            text = data.get('text', '')
            
            # Parse doc_id: dialogue_剧情_新剧本测试_1_1_0
            parts = doc_id.split('_')
            if len(parts) >= 6:
                quest_type = parts[1]
                quest_name = parts[2]
                quest_id = parts[3]
                section_id = parts[4]
                dialogue_id = parts[5]
                
                # Build new data structure
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
                
                # Try to get more info from TextMap
                for key, value in textmap.items():
                    if key.startswith(f"QuestChapter_{quest_id}_"):
                        if "ChapterName" in key:
                            cleaned_item['chapter_title'] = value
                        elif "ChapterNum" in key:
                            cleaned_item['section_title'] = value
                        elif "SectionNum" in key:
                            cleaned_item['section_desc'] = value
                
                # Find quest description
                quest_desc_key = f"Quest_{quest_id}000025_QuestDesc_0_2"
                if quest_desc_key in textmap:
                    cleaned_item['quest_desc'] = textmap[quest_desc_key]
                
                # Find child quest tip
                child_tip_key = f"Quest_{quest_id}000025_ChildQuestTip_0_{dialogue_id}"
                if child_tip_key in textmap:
                    cleaned_item['child_tip'] = textmap[child_tip_key]
                
                cleaned_data.append(cleaned_item)
            
        except json.JSONDecodeError as e:
            print(f"Line {i+1} JSON error: {e}")
            continue
    
    # Save cleaned data
    output_file = "WutheringDialog/data/dialogs_zh-Hans.cleaned.jsonl"
    print(f"Saving cleaned data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in cleaned_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Cleaning complete! Processed {len(cleaned_data)} records")
    
    # Show examples
    print("Sample cleaned data:")
    for i, item in enumerate(cleaned_data[:2]):
        print(f"Sample {i+1}:")
        print(f"  doc_id: {item['doc_id']}")
        print(f"  chapter_title: {item['chapter_title']}")
        print(f"  section_title: {item['section_title']}")
        print(f"  quest_desc: {item['quest_desc']}")
        print(f"  child_tip: {item['child_tip']}")
        print(f"  text: {item['text'][:50]}...")

if __name__ == "__main__":
    clean_dialogue_data()
