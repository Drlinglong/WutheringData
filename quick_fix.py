#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def quick_fix():
    print("=== Quick Fix for Missing Quest Info ===")
    
    # 加载TextMap
    with open("TextMap/zh-Hans/MultiText.json", 'r', encoding='utf-8') as f:
        textmap = json.load(f)
    
    # 检查quest_id 135000001
    quest_id = 135000001
    quest_keys = [k for k in textmap.keys() if f'Quest_{quest_id}_' in k]
    
    print(f"Quest {quest_id} keys:")
    for key in quest_keys[:10]:
        print(f"  {key}: {textmap[key]}")
    
    # 查找章节信息
    print(f"\nLooking for chapter info...")
    chapter_keys = [k for k in textmap.keys() if k.startswith("QuestChapter_")]
    print(f"Found {len(chapter_keys)} chapter keys")
    
    # 查找包含"中曲台地"的章节
    zhongqu_keys = [k for k in chapter_keys if "中曲台地" in textmap[k]]
    print(f"Keys containing '中曲台地': {len(zhongqu_keys)}")
    for key in zhongqu_keys:
        print(f"  {key}: {textmap[key]}")

if __name__ == "__main__":
    quick_fix()

