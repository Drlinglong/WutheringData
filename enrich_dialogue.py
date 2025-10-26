
import json
import os
import re
from collections import defaultdict

def find_playflow_actions(node_data):
    """Recursively finds all PlayFlow actions within a node's actions."""
    playflows = []
    if isinstance(node_data, dict):
        # Check for PlayFlow in EnterActions or FinishActions
        for action_list_key in ['EnterActions', 'FinishActions']:
            if action_list_key in node_data:
                for action in node_data[action_list_key]:
                    if action.get('Name') == 'PlayFlow':
                        playflows.append(action)
        
        # Recursively check in children nodes
        if 'Children' in node_data:
            for child in node_data['Children']:
                playflows.extend(find_playflow_actions(child))
        
        if 'Child' in node_data:
            playflows.extend(find_playflow_actions(node_data['Child']))
            
        if 'Slots' in node_data:
            for slot in node_data['Slots']:
                if 'Node' in slot:
                    playflows.extend(find_playflow_actions(slot['Node']))

    return playflows

def enrich_dialogues(config_dir, text_map_path, dialog_path, output_path):
    """
    Enriches dialogue file with subtitles from LevelPlayNodeData.
    """
    print("Starting dialogue enrichment process...")
    try:
        with open(os.path.join(config_dir, "LevelPlayNodeData.json"), 'r', encoding='utf-8') as f:
            level_play_nodes = json.load(f)
        with open(text_map_path, 'r', encoding='utf-8') as f:
            text_map = json.load(f)
    except FileNotFoundError as e:
        print(f"ERROR: Required file not found - {e}")
        return

    # --- Step 1: Build the mapping from Dialogue Title to Subtitle Text ---
    dialogue_to_subtitle = {}
    print("Building map from LevelPlayNodeData.json...")
    for node in level_play_nodes:
        try:
            data_str = node.get("Data", "{}")
            node_data = json.loads(data_str)
        except json.JSONDecodeError:
            continue

        subtitle_key = node_data.get('TidTip')
        if not subtitle_key:
            continue

        playflow_actions = find_playflow_actions(node_data)
        
        # If there are PlayFlow actions associated with this subtitle
        if playflow_actions:
            subtitle_text = text_map.get(subtitle_key)
            if not subtitle_text:
                continue

            for action in playflow_actions:
                params = action.get('Params', {})
                flow_list_name = params.get('FlowListName')
                flow_id = params.get('FlowId')
                state_id = params.get('StateId')

                if all([flow_list_name, flow_id is not None, state_id is not None]):
                    dialogue_title = f"{flow_list_name}_{flow_id}_{state_id}"
                    dialogue_to_subtitle[dialogue_title] = subtitle_text
    
    print(f"Map built. Found {len(dialogue_to_subtitle)} subtitle-to-dialogue mappings.")

    # --- Step 2: Enrich dialogues and write to new file ---
    enriched_count = 0
    total_lines = 0
    try:
        with open(dialog_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                total_lines += 1
                try:
                    record = json.loads(line)
                    title = record.get('title')

                    subtitle = dialogue_to_subtitle.get(title)
                    if subtitle:
                        # Find the first dialog action and prepend the subtitle
                        is_enriched = False
                        for action in record.get('actions', []):
                            if 'dialogs' in action and action['dialogs']:
                                first_dialog = action['dialogs'][0]
                                original_content = first_dialog.get('content', '')
                                first_dialog['content'] = f"[小标题：{subtitle}]\n\n{original_content}"
                                enriched_count += 1
                                is_enriched = True
                                break # Enrich only the first dialog block
                        
                    outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
                except json.JSONDecodeError:
                    outfile.write(line) # Write non-json lines as-is
                    continue

        print(f"Enrichment complete. Processed {total_lines} lines.")
        print(f"Added subtitles to {enriched_count} dialogue records.")
        print(f"New file created at: {output_path}")

    except FileNotFoundError:
        print(f"ERROR: Dialogue file not found at {dialog_path}")

if __name__ == "__main__":
    config_directory = "ConfigDB"
    text_map_file = "TextMap/zh-Hans/MultiText.json"
    dialogue_file = "WutheringDialog/data/dialogs_zh-Hans.cleaned.jsonl"
    output_file = "WutheringDialog/data/dialogs_zh-Hans.enriched.jsonl"
    enrich_dialogues(config_directory, text_map_file, dialogue_file, output_file)
