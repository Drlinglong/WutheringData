import json
import os
import re
from collections import defaultdict

MIN_TEXT_LENGTH = 200 # Minimum character count for a valid character document

def clean_text(text):
    """Removes simple HTML-like tags from the text."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<te[^>]*>', '', text)
    text = re.sub(r'</te>', '', text)
    text = re.sub(r'<ano=[^>]*>', '', text)
    text = re.sub(r'</ano>', '', text)
    text = text.replace("<br>", "\n")
    return text.strip()

def process_characters_from_textmap(text_map_path, output_path):
    """
    Extracts, cleans, and unifies character info, then de-duplicates and filters by length.
    """
    try:
        with open(text_map_path, 'r', encoding='utf-8') as f:
            text_map = json.load(f)
    except FileNotFoundError:
        print(f"Error: Text map file not found at {text_map_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {text_map_path}")
        return

    rover_gender_map = {
        "1406": "男", "1408": "女", # 气动
        "1501": "男", "1502": "女", # 衍射
        "1604": "男", "1605": "女"  # 湮灭
    }
    blacklist_names = {
        "dnt/叮咚咚", "dnt/流放者", "dnt/炮台", "dnt/骑士", "dnt/鳞人",
        "吟霖人偶", "咕咕河豚", "坚岩斗士", "处决用女主", "处决用男主",
        "游弋蝶", "遁地鼠", "无冠者", "岁光"
    }

    characters_data = defaultdict(dict)
    key_regex = re.compile(r"^(RoleInfo|FavorRoleInfo|FavorStory|FavorWord)_(\d+)_(\w+)")
    for key, value in text_map.items():
        match = key_regex.match(key)
        if match:
            full_id_str = match.group(2)
            if len(full_id_str) >= 4:
                char_id = full_id_str[:4]
                characters_data[char_id][key] = value

    # --- Step 1: Process all potential characters into a temporary list ---
    processed_records = defaultdict(list)
    for char_id, data in characters_data.items():
        name = data.get(f"RoleInfo_{char_id}_Name")
        if not name or name in blacklist_names:
            continue
        
        title = data.get(f"RoleInfo_{char_id}_NickName", "")
        if "声骸角色" in title:
            continue

        if name == "椿":
            name = "樁"
        
        if name.startswith("漂泊者"):
            element = name.split("·")[-1]
            gender_char = rover_gender_map.get(char_id, "未知")
            name = f"漂泊者-{gender_char}-{element}"

        doc_text = f"角色名称: {name}\n"
        if title and "存在异常" not in title:
            doc_text += f"称号: {title}\n"

        bio = data.get(f"FavorRoleInfo_{char_id}_Info")
        if bio:
            doc_text += "\n-----角色资料-----" + clean_text(bio) + "\n"

        stories = defaultdict(dict)
        story_regex = re.compile(r"FavorStory_(\d+)_(\w+)")
        for key, value in data.items():
            match = story_regex.match(key)
            if match and key.startswith(f"FavorStory_{char_id}"):
                stories[match.group(1)][match.group(2)] = value
        
        if stories:
            doc_text += "\n-----角色故事-----"
            for story_id in sorted(stories.keys()):
                story_title = stories[story_id].get("Title", "")
                story_content = stories[story_id].get("Content", "")
                if story_title and story_content:
                    doc_text += f"\n标题: {clean_text(story_title)}\n{clean_text(story_content)}\n"

        words = defaultdict(dict)
        word_regex = re.compile(r"FavorWord_(\d+)_(\w+)")
        for key, value in data.items():
            match = word_regex.match(key)
            if match and key.startswith(f"FavorWord_{char_id}"):
                words[match.group(1)][match.group(2)] = value

        if words:
            doc_text += "\n-----心声-----"
            for word_id in sorted(words.keys()):
                word_title = words[word_id].get("Title", "")
                word_content = words[word_id].get("Content", "")
                if word_title and word_content:
                    doc_text += f"\n标题: {clean_text(word_title)}\n{clean_text(word_content)}\n"

        json_record = {
            "doc_id": f"character_{char_id}",
            "text": doc_text.strip(),
            "metadata": {"source": "Character", "type": "角色", "name": name, "id": int(char_id)}
        }
        
        # Group records by the final, unified name
        processed_records[name].append(json_record)

    # --- Step 2: De-duplicate and filter by length ---
    final_records = []
    for name, records in processed_records.items():
        # If there are duplicates, find the one with the longest text
        best_record = max(records, key=lambda r: len(r['text']))
        
        # Apply the minimum length threshold
        if len(best_record['text']) >= MIN_TEXT_LENGTH:
            final_records.append(best_record)
        else:
            print(f"INFO: Discarding character '{name}' due to short text length ({len(best_record['text'])} chars).")
    # --- Step 3: Write final, clean records to file ---
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for record in sorted(final_records, key=lambda r: r['metadata']['id']):
            outfile.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f"Successfully de-duplicated, filtered, and wrote {len(final_records)} characters to {output_path}")

if __name__ == "__main__":
    text_map_file = "TextMap/zh-Hans/MultiText.json"
    # 创建output目录
    import os
    if not os.path.exists("../output"):
        os.makedirs("../output")
    
    output_file = "../output/characters.jsonl"
    process_characters_from_textmap(text_map_file, output_file)
