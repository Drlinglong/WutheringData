#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def check_sample_data():
    print("Checking sample data...")
    
    with open('WutheringDialog/data/dialogs_zh-Hans.fixed_final.jsonl', 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 20:
                break
            try:
                data = json.loads(line.strip())
                print(f"Line {i+1}: quest_name='{data['quest_name']}', quest_id={data['quest_id']}")
            except json.JSONDecodeError:
                continue

if __name__ == "__main__":
    check_sample_data()
