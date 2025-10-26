import json
import os

def structure_for_rag(input_file, output_file):
    """
    Reads the cleaned JSONL file and transforms it into a RAG-friendly
    format, where each line is a document ready for chunking and embedding.
    """
    print(f"Starting structuring process...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")

    lines_processed = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                data = json.loads(line)
                title = data.get('title', '')
                
                if not title:
                    continue

                full_text = []
                action_ids = []

                for action in data.get('actions', []):
                    action_id = action.get('id')
                    if action_id:
                        action_ids.append(action_id)

                    if 'dialogs' in action:
                        for dialog in action.get('dialogs', []):
                            role = dialog.get('role', '旁白').strip()
                            content = dialog.get('content', '').strip()
                            
                            # Handle player options, which have a different structure
                            if dialog.get('type') == 'option' and isinstance(content, list):
                                options_text = " [玩家选项: " + " / ".join([opt.get('content', '') for opt in content]) + "]"
                                full_text.append(options_text)
                            elif content:
                                if role:
                                    full_text.append(f"{role}: {content}")
                                else: # For plot narration
                                    full_text.append(content)
                
                if full_text:
                    # Create the final text block for this document
                    document_text = "\n".join(full_text)
                    
                    # Create the RAG-ready JSON object
                    rag_doc = {
                        "doc_id": title,  # Use the unique title as the document ID
                        "text": document_text,
                        "metadata": {
                            "source_title": title,
                            "action_ids": action_ids
                        }
                    }
                    
                    outfile.write(json.dumps(rag_doc, ensure_ascii=False) + '\n')
                    lines_processed += 1

        print(f"Structuring complete.")
        print(f"Total documents created: {lines_processed}")

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, 'data', 'dialogs_zh-Hans.cleaned.jsonl')
    output_path = os.path.join(script_dir, 'data', 'rag_input.jsonl')
    
    structure_for_rag(input_path, output_path)
