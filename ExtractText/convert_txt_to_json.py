import os
import json

def parse_subtitle_block(lines, start_idx):
    """Parses a block of subtitle lines into a dictionary."""
    block = {"id": "", "jp": "", "en": "", "ru": ""}
    i = start_idx
    while i < len(lines) and lines[i].strip():
        line = lines[i].strip()
        if line.startswith("ID:"):
            block["id"] = line[3:].strip()
        elif line.startswith("JP:"):
            block["jp"] = line[3:].strip()
        elif line.startswith("EN:"):
            block["en"] = line[3:].strip()
        elif line.startswith("RU:"):
            block["ru"] = line[3:].strip()
        i += 1
    return block, i

def convert_txt_to_json(txt_path, json_path):
    """Converts a TXT file to a JSON file with debug output."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        subtitles = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("ID:"):
                print(f"Processing block starting at line {i + 1}: {line}")
                block, next_i = parse_subtitle_block(lines, i)
                if block["id"]:  # Only append if ID is present
                    subtitles.append(block)
                i = next_i
            else:
                i += 1  # Move to next line even if no ID is found
        
        if not subtitles:
            print(f"No valid subtitle blocks found in {txt_path}")
        else:
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(subtitles, f, ensure_ascii=False, indent=4)
            print(f"Converted {txt_path} to {json_path} with {len(subtitles)} subtitle(s)")
    except Exception as e:
        print(f"Error converting {txt_path}: {str(e)}")

def main():
    input_dir = "nier_unpacked_extracted_result"
    output_dir = "nier_text_json"
    if not os.path.exists(input_dir):
        print(f"Error: {input_dir} not found.")
        return

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_path = os.path.join(root, file)
                # Preserve relative path structure in output directory
                relative_path = os.path.relpath(root, input_dir)
                json_output_dir = os.path.join(output_dir, relative_path)
                json_file = os.path.splitext(file)[0] + '.json'
                json_path = os.path.join(json_output_dir, json_file)
                convert_txt_to_json(txt_path, json_path)

    print(f"\nConversion completed. Check {os.path.abspath(output_dir)} for .json files.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()