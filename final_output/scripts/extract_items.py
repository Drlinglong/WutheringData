
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

def extract_items(text_map_path, output_path):
    """
    Extracts item data from the master text map based on the 'ItemInfo_' prefix.
    """
    print(f"Starting to extract item data from {text_map_path}...")
    try:
        with open(text_map_path, 'r', encoding='utf-8') as f:
            text_map = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Input file not found at {text_map_path}")
        return

    # --- Group data for all items based on the ItemInfo_ prefix ---
    items_data = defaultdict(dict)
    key_regex = re.compile(r"ItemInfo_(\d+)_(\w+)")
    for key, value in text_map.items():
        match = key_regex.match(key)
        if match:
            item_id = match.group(1)
            field = match.group(2)
            items_data[item_id][field] = value

    print(f"Found {len(items_data)} potential item entries.")

    # --- Process and write each item to the output file ---
    processed_count = 0
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for item_id, data in sorted(items_data.items()):
            name = data.get("Name")
            if not name or "test" in name.lower() or "dnt" in name.lower():
                continue

            # Assemble the document text
            doc_text = f"物品名称: {name}\n"
            
            # Functional Description
            func_desc = data.get("AttributesDescription")
            if func_desc:
                doc_text += f"\n-----功能描述-----\n{clean_text(func_desc)}\n"

            # Background Story
            bg_desc = data.get("BgDescription")
            if bg_desc and bg_desc != func_desc:
                doc_text += f"\n-----背景故事-----\n{clean_text(bg_desc)}\n"

            # Obtained Description (if different from the others)
            obt_desc = data.get("ObtainedShowDescription")
            if obt_desc and obt_desc != func_desc and obt_desc != bg_desc:
                 doc_text += f"\n-----获取描述-----\n{clean_text(obt_desc)}\n"

            # Skip items with only a name
            if len(doc_text) < (len(name) + 20):
                continue

            # Create the JSONL record
            record = {
                "doc_id": f"item_{item_id}",
                "text": doc_text.strip(),
                "metadata": {
                    "source": "Item",
                    "type": "物品",
                    "name": name,
                    "id": int(item_id)
                }
            }
            outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
            processed_count += 1

    print(f"Successfully extracted and wrote {processed_count} items to {output_path}")

if __name__ == "__main__":
    text_map_file = "TextMap/zh-Hans/MultiText.json"
    output_file = "WutheringDialog/data/items.jsonl"
    extract_items(text_map_file, output_file)
