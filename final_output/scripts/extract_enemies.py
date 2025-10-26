
import json
import re
from collections import defaultdict

def clean_text(text):
    """Removes simple HTML-like tags from the text."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace("<br>", "\n")
    return text.strip()

def extract_enemies(text_map_path, output_path):
    """
    Extracts enemy data from the master text map based on the 'MonsterInfo_' prefix.
    """
    print(f"Starting to extract enemy data from {text_map_path}...")
    try:
        with open(text_map_path, 'r', encoding='utf-8') as f:
            text_map = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Input file not found at {text_map_path}")
        return

    # --- Group data for all enemies based on the MonsterInfo_ prefix ---
    enemies_data = defaultdict(dict)
    key_regex = re.compile(r"MonsterInfo_(\d+)_(\w+)")
    for key, value in text_map.items():
        match = key_regex.match(key)
        if match:
            enemy_id = match.group(1)
            field = match.group(2)
            enemies_data[enemy_id][field] = value

    print(f"Found {len(enemies_data)} potential enemy entries.")

    # --- Process and write each enemy to the output file ---
    processed_count = 0
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for enemy_id, data in sorted(enemies_data.items()):
            name = data.get("Name")
            if not name or "test" in name.lower() or "dnt" in name.lower():
                continue

            # Assemble the document text
            doc_text = f"敌人名称: {name}\n"
            
            # Undiscovered Description
            undisc_desc = data.get("UndiscoveredDes")
            if undisc_desc:
                doc_text += f"\n-----基本描述-----\n{clean_text(undisc_desc)}\n"

            # Discovered Description (main info)
            disc_desc = data.get("DiscoveredDes")
            if disc_desc:
                doc_text += f"\n-----详细信息-----\n{clean_text(disc_desc)}\n"

            # Skip entries with only a name
            if len(doc_text) < (len(name) + 20):
                continue

            # Create the JSONL record
            record = {
                "doc_id": f"enemy_{enemy_id}",
                "text": doc_text.strip(),
                "metadata": {
                    "source": "Enemy",
                    "type": "敌人",
                    "name": name,
                    "id": int(enemy_id)
                }
            }
            outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
            processed_count += 1

    print(f"Successfully extracted and wrote {processed_count} enemies to {output_path}")

if __name__ == "__main__":
    text_map_file = "TextMap/zh-Hans/MultiText.json"
    output_file = "WutheringDialog/data/enemies.jsonl"
    extract_enemies(text_map_file, output_file)
