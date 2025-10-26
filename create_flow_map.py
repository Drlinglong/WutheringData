
import json
import os

def create_flow_map(config_dir, output_path):
    """
    Creates a mapping from a dialogue StateKey to its parent FlowId.
    Example: {"剧情_新剧本测试_1_1": "剧情_新剧本测试_1"}
    """
    flow_file_path = os.path.join(config_dir, "Flow.json")
    print(f"Reading {flow_file_path} to create flow map...")

    try:
        with open(flow_file_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {flow_file_path} not found.")
        return

    state_to_flow_map = {}
    for flow in flow_data:
        flow_id = flow.get("Id")
        states = flow.get("States")
        if not all([flow_id, states]):
            continue
        
        for state in states:
            # Construct the StateKey, e.g., "剧情_新剧本测试_1" + "_" + 1 -> "剧情_新剧本测试_1_1"
            state_key = f"{flow_id}_{state}"
            state_to_flow_map[state_key] = flow_id

    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            json.dump(state_to_flow_map, outfile, ensure_ascii=False, indent=2)
        print(f"Successfully created flow map with {len(state_to_flow_map)} entries.")
        print(f"Map saved to: {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to write to output file {output_path}: {e}")

if __name__ == "__main__":
    config_directory = "ConfigDB"
    # We'll save our generated maps in the data directory
    output_file = "WutheringDialog/data/flow_map.json"
    create_flow_map(config_directory, output_file)
