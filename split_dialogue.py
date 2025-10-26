
import json
import os

def split_dialogue_file(input_path, output_path):
    """Splits dialogue records into single-sentence records."""
    print(f"Starting to split dialogue file: {input_path}...")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"ERROR: Input file not found at {input_path}")
        return

    new_records = []
    total_original_records = len(lines)

    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            # If a line is not JSON, we might just skip it or write it as is.
            # For this task, we assume all lines are valid JSON from our previous steps.
            continue

        original_title = record.get('title', 'unknown_title')
        actions = record.get('actions', [])

        for action in actions:
            dialogs = action.get('dialogs')
            if isinstance(dialogs, list) and dialogs:
                # Found a dialog block, now split it
                for i, dialog_line in enumerate(dialogs):
                    role = dialog_line.get('role', '旁白') # Default to Narrator
                    content = dialog_line.get('content', '')

                    # Create a new record for each line of dialogue
                    new_doc_id = f"dialogue_{original_title}_{i}"
                    new_text = f"{role}: {content}"
                    
                    new_record = {
                        "doc_id": new_doc_id,
                        "text": new_text
                    }
                    new_records.append(new_record)
                
                # We only process the first valid dialog block found in an action list
                break

    # Write all the new, fine-grained records to the output file
    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for record in new_records:
                outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"Successfully split {total_original_records} dialogue records into {len(new_records)} single-sentence records.")
        print(f"New file created at: {output_path}")

    except Exception as e:
        print(f"ERROR: Failed to write to output file: {e}")

if __name__ == "__main__":
    input_file = "WutheringDialog/data/dialogs_zh-Hans.enriched.jsonl"
    output_file = "WutheringDialog/data/dialogs_zh-Hans.split.jsonl"
    split_dialogue_file(input_file, output_file)
