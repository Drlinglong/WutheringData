import json
import os
from collections import defaultdict

def get_text(text_map, key, default=""):
    """Safely retrieves text from the text map."""
    return text_map.get(key, default)

def extract_achievements_individual(config_dir, text_map_path, output_path):
    """
    Extracts each achievement as a separate document.
    """
    print(f"Starting to extract individual achievements...")
    try:
        with open(os.path.join(config_dir, "Achievement.json"), 'r', encoding='utf-8') as f:
            achievements = json.load(f)
        with open(os.path.join(config_dir, "AchievementGroup.json"), 'r', encoding='utf-8') as f:
            achievement_groups = json.load(f)
        with open(text_map_path, 'r', encoding='utf-8') as f:
            text_map = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: Required file not found - {e}")
        return

    # --- Create a map of Group ID to Group Name ---
    group_id_to_name = {
        group['Id']: get_text(text_map, group['Name'])
        for group in achievement_groups
    }

    # --- Process and write each achievement individually ---
    processed_count = 0
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for ach in achievements:
            ach_name = get_text(text_map, ach.get('Name'))
            ach_desc = get_text(text_map, ach.get('Desc'))

            # Filter out invalid or test achievements
            if not all([ach_name, ach_desc]) or "test" in ach_name.lower() or "dnt" in ach_name.lower():
                continue

            group_id = ach.get('GroupId')
            group_name = group_id_to_name.get(group_id, "未知组别")

            # Assemble the document text for the single achievement
            doc_text = f"成就组: {group_name}\n\n"
            doc_text += f"成就: {ach_name}\n"
            doc_text += f"描述: {ach_desc}"

            # Create the JSONL record
            record = {
                "doc_id": f"achievement_{ach['Id']}",
                "text": doc_text.strip(),
                "metadata": {
                    "source": "Achievement",
                    "type": "成就",
                    "name": ach_name,
                    "group": group_name,
                    "id": ach['Id']
                }
            }
            outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
            processed_count += 1

    print(f"Successfully extracted and wrote {processed_count} individual achievements to {output_path}")

if __name__ == "__main__":
    config_directory = "ConfigDB"
    text_map_file = "TextMap/zh-Hans/MultiText.json"
    output_file = "WutheringDialog/data/achievements.jsonl"
    extract_achievements_individual(config_directory, text_map_file, output_file)
