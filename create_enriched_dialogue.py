
import json
import os
import ijson

def load_json_data(file_path):
    """Loads a JSON file."""
    if not os.path.exists(file_path):
        print(f"Warning: File not found at {file_path}, returning empty dict.")
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_speaker_name(speaker_id, speakers_map):
    """Gets speaker name from speaker ID."""
    return speakers_map.get(str(speaker_id), "旁白")

def main():
    repo_path = "J:\\综合性AI\\WutheringData"
    lang = "zh-Hans"
    output_file = os.path.join(repo_path, "dialogs_zh-Hans.enriched.jsonl")

    # Load mapping files
    print("Loading mapping files...")
    text_map = load_json_data(os.path.join(repo_path, f"TextMap/{lang}/MultiText.json"))
    speaker_map_raw = load_json_data(os.path.join(repo_path, f"TextMap/{lang}/Speaker.json"))
    speakers = {v: k for k, v in speaker_map_raw.items()} # Invert for easier lookup

    quests_map = {str(q['Id']): q for q in load_json_data(os.path.join(repo_path, "ConfigDB/Quest.json"))}
    adv_tasks_map = {str(t['Id']): t for t in load_json_data(os.path.join(repo_path, "ConfigDB/AdventureTask.json"))}
    quest_chapter_map = {str(c['Id']): c for c in load_json_data(os.path.join(repo_path, "ConfigDB/QuestChapter.json"))}
    adv_task_text_map = load_json_data(os.path.join(repo_path, f"TextMap/{lang}/AdventureTask.json"))

    # --- Create a reverse mapping from Flow ID (StateKey) to Quest info ---
    # This is the most complex part as the link is not direct.
    # We will build a heuristic-based map. A flow's name often contains quest info.
    print("Building reverse mapping from Flow to Quest...")
    flow_to_quest_map = {}
    all_flows = load_json_data(os.path.join(repo_path, "ConfigDB/Flow.json"))
    for flow in all_flows:
        flow_id = flow.get("Id")
        if not flow_id:
            continue
        # Heuristic: Try to match flow ID with quest keys or names
        for quest_id, quest in quests_map.items():
            quest_key = quest.get("QuestKey", "")
            # Example: Flow "剧情_新主线_第五章1_1" and QuestKey "Main_Chapter5_1"
            # This requires a smart matching logic. For now, we'll do a simple substring search.
            # A more robust solution might need regex or more detailed mapping.
            if quest_key and quest_key in flow_id:
                 flow_to_quest_map[flow_id] = quests_map.get(quest_id)
                 break # Found a match, move to next flow

    print(f"Mapped {len(flow_to_quest_map)} flows to quests.")

    # --- Process the large FlowState.json file ---
    flow_state_path = os.path.join(repo_path, "ConfigDB/FlowState.json")
    print(f"Starting to process {flow_state_path}...")

    enriched_records = []
    
    with open(flow_state_path, 'r', encoding='utf-8') as f:
        flow_states = ijson.items(f, 'item')
        for i, flow in enumerate(flow_states):
            state_key = flow.get("StateKey")
            if not state_key:
                continue

            # Find context for this flow
            chapter_title = "Unknown Chapter"
            chapter_desc = "Unknown Chapter Description"
            section_title = "Unknown Section"
            section_desc = "Unknown Section Description"

            # Use the pre-built map to find the quest
            quest_info = flow_to_quest_map.get(state_key)
            if quest_info:
                chapter_title = quest_info.get("QuestName", chapter_title)
                chapter_desc = quest_info.get("QuestText", chapter_desc)
                
                # Now try to find section info via AdventureTask
                # This link is still weak. Let's assume the flow IS the section for now.
                section_title = state_key # Use the flow's own ID as a fallback title
                
            # Process actions in the flow
            try:
                actions = json.loads(flow.get("Actions", "[]"))
            except json.JSONDecodeError:
                continue

            dialogue_index = 0
            for action in actions:
                if "Params" not in action or "TalkItems" not in action["Params"]:
                    continue
                
                for talk in action["Params"]["TalkItems"]:
                    if "TidTalk" in talk:
                        speaker_id = talk.get("WhoId")
                        speaker_name = speakers.get(str(speaker_id), "旁白")
                        content = text_map.get(talk["TidTalk"], "")
                        
                        if content:
                            doc_id = f"dialogue_{state_key}_{dialogue_index}"
                            text = f"{speaker_name}: {content}"
                            
                            record = {
                                "doc_id": doc_id,
                                "chapter_title": chapter_title,
                                "chapter_desc": chapter_desc,
                                "section_title": section_title,
                                "section_desc": section_desc,
                                "text": text
                            }
                            enriched_records.append(record)
                            dialogue_index += 1

            if i % 500 == 0 and i > 0:
                print(f"Processed {i} flow states...")

    # Write to output file
    print(f"Writing {len(enriched_records)} enriched records to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        for record in enriched_records:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    print("Done.")

if __name__ == "__main__":
    main()
