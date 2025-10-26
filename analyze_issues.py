#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from collections import defaultdict

def analyze_mapping_issues():
    print("=== ANALYZING MAPPING ISSUES ===")
    
    # 统计各种问题
    stats = {
        'total': 0,
        'null_quest_id': 0,
        'empty_quest_name': 0,
        'empty_chapter_title': 0,
        'empty_section_title': 0,
        'empty_section_desc': 0,
        'flow_patterns': defaultdict(int),
        'quest_id_patterns': defaultdict(int)
    }
    
    with open('WutheringDialog/data/dialogs_zh-Hans.final_corrected.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                stats['total'] += 1
                
                # 检查quest_id
                if data['quest_id'] is None:
                    stats['null_quest_id'] += 1
                else:
                    quest_id_str = str(data['quest_id'])
                    if quest_id_str.startswith('135'):
                        stats['quest_id_patterns']['135'] += 1
                    elif quest_id_str.startswith('139'):
                        stats['quest_id_patterns']['139'] += 1
                    elif quest_id_str.startswith('140'):
                        stats['quest_id_patterns']['140'] += 1
                    elif quest_id_str.startswith('114'):
                        stats['quest_id_patterns']['114'] += 1
                    else:
                        stats['quest_id_patterns']['other'] += 1
                
                # 检查quest_name
                if data['quest_name'] == '' or data['quest_name'] == 'Unknown':
                    stats['empty_quest_name'] += 1
                
                # 检查chapter_title
                if data['chapter_title'] == '' or data['chapter_title'] == 'Unknown':
                    stats['empty_chapter_title'] += 1
                
                # 检查section_title
                if data['section_title'] == '' or data['section_title'] == 'Unknown':
                    stats['empty_section_title'] += 1
                
                # 检查section_desc
                if data['section_desc'] == '' or data['section_desc'] == 'Unknown':
                    stats['empty_section_desc'] += 1
                
                # 分析flow模式
                doc_id = data['doc_id']
                if doc_id.startswith('dialogue_'):
                    flow_part = doc_id[9:]  # 去掉 'dialogue_' 前缀
                    parts = flow_part.split('_')
                    if len(parts) >= 2:
                        flow_prefix = '_'.join(parts[:2])  # 取前两部分作为flow模式
                        stats['flow_patterns'][flow_prefix] += 1
                
            except json.JSONDecodeError:
                continue
    
    print(f"Total records: {stats['total']}")
    print(f"Null quest_id: {stats['null_quest_id']} ({stats['null_quest_id']/stats['total']*100:.1f}%)")
    print(f"Empty quest_name: {stats['empty_quest_name']} ({stats['empty_quest_name']/stats['total']*100:.1f}%)")
    print(f"Empty chapter_title: {stats['empty_chapter_title']} ({stats['empty_chapter_title']/stats['total']*100:.1f}%)")
    print(f"Empty section_title: {stats['empty_section_title']} ({stats['empty_section_title']/stats['total']*100:.1f}%)")
    print(f"Empty section_desc: {stats['empty_section_desc']} ({stats['empty_section_desc']/stats['total']*100:.1f}%)")
    
    print("\nQuest ID patterns:")
    for pattern, count in sorted(stats['quest_id_patterns'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {pattern}: {count}")
    
    print("\nTop flow patterns:")
    sorted_flows = sorted(stats['flow_patterns'].items(), key=lambda x: x[1], reverse=True)
    for flow, count in sorted_flows[:20]:
        print(f"  {flow}: {count}")
    
    print("\nUnmapped flow patterns (likely causing null quest_id):")
    unmapped_flows = []
    for flow, count in sorted_flows:
        if count > 100 and ('生态' in flow or 'NPC' in flow or '测试' in flow or '玩法' in flow):
            unmapped_flows.append((flow, count))
    
    for flow, count in unmapped_flows[:10]:
        print(f"  {flow}: {count}")

if __name__ == "__main__":
    analyze_mapping_issues()
