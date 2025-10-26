#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_text_matching():
    # 从文件中读取实际的文本
    import json
    
    with open('WutheringDialog/data/dialogs_zh-Hans.final_corrected.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                if data['doc_id'] == 'dialogue_剧情_剧情_角色_吟霖线新_25_1_5':
                    actual_text = data['text']
                    print("Actual text:", repr(actual_text))
                    
                    # 我之前的映射
                    my_mapping = "何昌他也是夜归的士兵，是我的搭档，他为了救我而陷入了重度超频之中……没能救回来。"
                    print("My mapping:", repr(my_mapping))
                    print("Match:", actual_text == my_mapping)
                    print("Contains:", my_mapping in actual_text)
                    break
            except json.JSONDecodeError:
                continue

if __name__ == "__main__":
    test_text_matching()
