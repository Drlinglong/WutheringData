#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def check_data_quality():
    print("Checking data quality...")
    
    total_count = 0
    quest_name_count = 0
    chapter_count = 0
    mapped_count = 0
    
    with open('WutheringDialog/data/dialogs_zh-Hans.fixed_final.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                total_count += 1
                
                if data['quest_id'] is not None:
                    mapped_count += 1
                
                if data['quest_name'] != 'Unknown' and data['quest_name'] != '':
                    quest_name_count += 1
                
                if data['chapter_title'] != '' and data['chapter_title'] != 'Unknown':
                    chapter_count += 1
                    
            except json.JSONDecodeError:
                continue
    
    print(f"Total dialogues: {total_count}")
    print(f"Mapped dialogues: {mapped_count}")
    print(f"Quest names found: {quest_name_count}")
    print(f"Chapters found: {chapter_count}")
    print(f"Mapping rate: {mapped_count/total_count*100:.1f}%")
    print(f"Quest name rate: {quest_name_count/total_count*100:.1f}%")
    print(f"Chapter rate: {chapter_count/total_count*100:.1f}%")
    
    if mapped_count > 0:
        print(f"Quest name rate (mapped only): {quest_name_count/mapped_count*100:.1f}%")
        print(f"Chapter rate (mapped only): {chapter_count/mapped_count*100:.1f}%")

if __name__ == "__main__":
    check_data_quality()
