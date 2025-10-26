import json
import re
import os
import sys

def sanitize_for_id(text):
    """Sanitizes a string to be used as a part of a doc_id."""
    sanitized = re.sub(r'[\s\\/:*?"<>|]+', '_', text)
    return sanitized.strip('_')

def split_rag_file(input_path, output_path):
    """Splits a coarse-grained RAG input file into fine-grained records."""
    print(f"Starting to split {input_path}...")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"ERROR: Input file not found at {input_path}")
        return

    new_records = []
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"WARNING: Skipping invalid JSON line: {line.strip()}")
            continue

        original_doc_id = record.get('doc_id', '')
        text = record.get('text', '')
        metadata = record.get('metadata', {})

        if not all([original_doc_id, text, metadata]):
            continue

        entity_name = metadata.get('name', 'unknown')
        entity_type_en = original_doc_id.split('_')[0]

        # Split by section headers like '-----...-----' or the '标题: ' delimiter
        # This regex looks for either a section header or a title
        parts = re.split(r'(?=\n-----|\n标题: )', text)
        
        if not parts:
            continue

        # Process each part as a separate record
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Determine the sub-topic identifier
            first_line = part.split('\n')[0]
            if first_line.startswith('-----'):
                # It's a section like -----技能描述-----
                sub_id_part = sanitize_for_id(first_line.strip('-'))
            elif first_line.startswith('标题: '):
                # It's a title
                sub_id_part = sanitize_for_id(first_line[3:].strip())
            else:
                # It's the base info (the very first part)
                sub_id_part = sanitize_for_id("资料")

            new_doc_id = f"{entity_type_en}_{entity_name}_{sub_id_part}"
            new_records.append({
                "doc_id": new_doc_id,
                "text": part
            })

    # Write to new file
    try:
        with open(output_path, 'w', encoding='utf-8') as outfile:
            for record in new_records:
                outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"Successfully split {len(lines)} records into {len(new_records)} fine-grained records.")
        print(f"New file created at: {output_path}")
    except Exception as e:
        print(f"ERROR: Failed to write to output file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_rag_input.py <input_file_path> <output_file_path>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        split_rag_file(input_file, output_file)