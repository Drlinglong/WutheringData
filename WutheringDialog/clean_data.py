import json
import os
import argparse

def clean_dialog_data(input_file, output_file):
    """
    Reads a JSONL file, filters out test/junk data, and writes the cleaned
    data to a new JSONL file.
    """
    print(f"Starting cleaning process...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")

    # Define junk content to be filtered out
    junk_content = {
        "DefaultState", 
        "1111111111111", 
        "2222222222222", 
        "333333333333333333", 
        "4444444444444444444"
    }
    
    lines_read = 0
    lines_written = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                lines_read += 1
                try:
                    data = json.loads(line)
                    
                    # Filter by title
                    title = data.get('title', '')
                    if 'Default' in title or 'InteractTest' in title:
                        continue

                    # Filter out actions with junk dialog content
                    valid_actions = []
                    for action in data.get('actions', []):
                        if 'dialogs' in action:
                            valid_dialogs = []
                            for dialog in action.get('dialogs', []):
                                content = dialog.get('content')
                                # Ensure content is a string and not junk
                                if isinstance(content, str) and content.strip() not in junk_content:
                                    valid_dialogs.append(dialog)
                            
                            if valid_dialogs:
                                action['dialogs'] = valid_dialogs
                                valid_actions.append(action)
                        else:
                            # Keep actions that are not dialogs (e.g., gameplay actions)
                            valid_actions.append(action)
                    
                    # If there are any valid actions left, write the cleaned data
                    if valid_actions:
                        data['actions'] = valid_actions
                        outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                        lines_written += 1

                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON line: {line.strip()}")
        
        print(f"Cleaning complete.")
        print(f"Total lines read: {lines_read}")
        print(f"Total lines written: {lines_written}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # Use a fixed path relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, 'data', 'dialogs_zh-Hans.jsonl')
    output_path = os.path.join(script_dir, 'data', 'dialogs_zh-Hans.cleaned.jsonl')
    
    clean_dialog_data(input_path, output_path)
