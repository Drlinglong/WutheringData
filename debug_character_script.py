
import json
import os
import re
from collections import defaultdict

def debug_character_extraction():
    """
    Runs the character extraction logic with verbose print statements for debugging.
    Does not write to any files.
    """
    print("--- STARTING DEBUG RUN ---")
    config_dir = "ConfigDB"
    text_map_path = "TextMap/zh-Hans/MultiText.json"

    try:
        with open(text_map_path, 'r', encoding='utf-8') as f:
            text_map = json.load(f)
        with open(os.path.join(config_dir, "RoleInfo.json"), 'r', encoding='utf-8') as f:
            role_infos = json.load(f)
        print("[SUCCESS] Loaded TextMap and RoleInfo.json")
    except Exception as e:
        print(f"[ERROR] Failed to load files: {e}")
        return

    # --- Prep ---
    gender_map = {role.get("Id"): role.get("Gender") for role in role_infos}
    gender_text_map = {1: "男", 2: "女"}
    blacklist_names = {
        "dnt/叮咚咚", "dnt/流放者", "dnt/炮台", "dnt/骑士", "dnt/鳞人",
        "吟霖人偶", "咕咕河豚", "坚岩斗士", "处决用女主", "处决用男主",
        "游弋蝶", "遁地鼠", "无冠者", "岁光"
    }

    # --- Grouping ---
    characters_data = defaultdict(dict)
    key_regex = re.compile(r"^(RoleInfo|FavorRoleInfo|FavorStory|FavorWord)_(\d+)_(\w+)")
    for key, value in text_map.items():
        match = key_regex.match(key)
        if match:
            full_id_str = match.group(2)
            if len(full_id_str) >= 4:
                char_id = full_id_str[:4]
                characters_data[char_id][key] = value
    print(f"[INFO] Grouped data for {len(characters_data)} potential character IDs.")

    # --- Processing Loop ---
    final_character_names = []
    print("\n--- Processing Individual Characters ---")
    for char_id, data in sorted(characters_data.items()):
        original_name = data.get(f"RoleInfo_{char_id}_Name")
        print(f"\nProcessing ID: {char_id} | Original Name: {original_name}")

        if not original_name:
            print("  - SKIPPING: No RoleInfo name found.")
            continue

        if original_name in blacklist_names:
            print(f"  - SKIPPING: Name '{original_name}' is in the blacklist.")
            continue
        
        title = data.get(f"RoleInfo_{char_id}_NickName", "")
        if "存在异常" in title or "声骸角色" in title:
            print(f"  - SKIPPING: Title '{title}' indicates abnormal data.")
            continue

        # --- Unification Logic ---
        unified_name = original_name
        if original_name == "椿":
            unified_name = "樁"
            print(f"  - UNIFYING: Renamed '{original_name}' to '{unified_name}'.")
        
        if original_name.startswith("漂泊者"):
            element = original_name.split("·")[-1]
            gender_id = gender_map.get(int(char_id))
            gender_char = gender_text_map.get(gender_id, "未知")
            unified_name = f"漂泊者-{gender_char}-{element}"
            print(f"  - UNIFYING: Renamed '{original_name}' to '{unified_name}' (Gender ID: {gender_id})")

        print(f"  - FINAL NAME: {unified_name}")
        final_character_names.append(unified_name)

    # --- Final Report ---
    print("\n--- DEBUG RUN COMPLETE ---")
    print(f"Successfully processed {len(final_character_names)} characters.")
    print("Final list of character names:")
    for name in sorted(final_character_names):
        print(f"  - {name}")

if __name__ == "__main__":
    debug_character_extraction()
