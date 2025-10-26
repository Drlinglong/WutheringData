
import json
import re
from collections import defaultdict

def clean_text(text):
    """Removes simple HTML-like tags from the text."""
    if not isinstance(text, str):
        return ""
    # This regex is simplified and might not cover all HTML-like tags.
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace("<br>", "\n")
    return text.strip()

def extract_weapons(text_map_path, output_path):
    """
    Extracts weapon data from the master text map and saves it to a dedicated file.
    """
    print(f"Starting to extract weapon data from {text_map_path}...")
    try:
        with open(text_map_path, 'r', encoding='utf-8') as f:
            text_map = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Input file not found at {text_map_path}")
        return

    # --- Step 1: Identify all valid weapon IDs first ---
    weapon_ids = set()
    id_regex = re.compile(r"WeaponConf_(\d+)_TypeDescription")
    for key, value in text_map.items():
        if value == "武器":
            match = id_regex.match(key)
            if match:
                weapon_ids.add(match.group(1))
    
    print(f"Found {len(weapon_ids)} unique weapon IDs.")

    # --- Step 2: Group data for all identified weapons ---
    weapons_data = defaultdict(dict)
    key_regex = re.compile(r"WeaponConf_(\d+)_(\w+)")
    for key, value in text_map.items():
        match = key_regex.match(key)
        if match:
            weapon_id = match.group(1)
            if weapon_id in weapon_ids:
                field = match.group(2)
                weapons_data[weapon_id][field] = value

    # --- Step 3: Process and write each weapon to the output file ---
    processed_count = 0
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for weapon_id, data in sorted(weapons_data.items()):
            name = data.get("WeaponName")
            if not name or "test" in name.lower():
                continue

            # Assemble the document text
            doc_text = f"武器名称: {name}\n"
            
            desc = data.get("Desc")
            if desc:
                doc_text += f"\n-----技能描述-----\n{clean_text(desc)}\n"

            # Use AttributesDescription for the story, fallback to BgDescription
            story = data.get("AttributesDescription") or data.get("BgDescription")
            if story:
                doc_text += f"\n-----武器故事-----\n{clean_text(story)}\n"

            # Create the JSONL record
            record = {
                "doc_id": f"weapon_{weapon_id}",
                "text": doc_text.strip(),
                "metadata": {
                    "source": "Weapon",
                    "type": "武器",
                    "name": name,
                    "id": int(weapon_id)
                }
            }
            outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
            processed_count += 1

    print(f"Successfully extracted and wrote {processed_count} weapons to {output_path}")

if __name__ == "__main__":
    text_map_file = "TextMap/zh-Hans/MultiText.json"
    output_file = "WutheringDialog/data/weapons.jsonl"
    extract_weapons(text_map_file, output_file)
