import json

def compare_character_lists():
    # List of names provided by the user from the community wiki
    wiki_names_list = [
        "嘉贝莉娜", "露帕", "干咲", "卜灵", "仇远", "奥古斯塔", "尤诺", "弗洛洛", 
        "卡提希娅", "夏空", "赞妮", "坎特蕾拉", "布兰特", "菲比", "洛可可", "珂莱塔", 
        "樁", "守岸人", "折枝", "相里要", "长离", "今汐", "吟霖", "忌炎", 
        "漂泊者-女-气动", "漂泊者-男-气动", "鉴心", "卡卡罗", "安可", "维里奈", 
        "凌阳", "漂泊者-男-衍射", "漂泊者-女-衍射", "漂泊者-男-湮灭", 
        "漂泊者-女-湮灭", "灯灯", "秧秧", "釉瑚", "白芷", "炽霞", "散华", 
        "秋水", "丹瑾", "莫特斐", "渊武", "桃祈"
    ]
    wiki_names = set(wiki_names_list)

    # Characters to ignore in the final comparison, as per user's investigation
    ignore_list = {"卜灵", "干咲"}

    # Path to the generated file
    input_file = "WutheringDialog/data/rag_input.jsonl"

    script_names = set()
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get("doc_id", "").startswith("character_"):
                        name = record.get("metadata", {}).get("name")
                        if name:
                            script_names.add(name)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found. Please run the extraction script first.")
        return

    # Find the final list of missing characters
    missing_from_script = wiki_names - script_names - ignore_list

    print("--- Final Gap Analysis ---")
    if missing_from_script:
        print(f"\n[!] Found {len(missing_from_script)} remaining missing characters:")
        for name in sorted(list(missing_from_script)):
            print(f"  - {name}")
    else:
        print("\n[+] All expected characters have been found!")

if __name__ == "__main__":
    compare_character_lists()