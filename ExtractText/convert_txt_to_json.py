import os
import json
import re

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

def parse_audio_text_lines(lines, start_idx):
    """Parses audio text lines, handling cases where text follows .wav on next line."""
    result = []
    i = start_idx
    while i < len(lines):
        line = lines[i].strip()
        if line.endswith(".wav"):
            entry = {"wav": line}
            i += 1
            # Collect text from the next non-empty line
            text_lines = []
            while i < len(lines) and not lines[i].strip().endswith(".wav"):
                text_lines.append(lines[i].strip())
                i += 1
            entry["text"] = " ".join(text_lines).strip() if text_lines else ""
            result.append(entry)
        else:
            i += 1
    return result, i

def detect_file_format(lines):
    """Detects if file is subtitle or audio text format based on first few lines."""
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line.startswith("ID:"):
            return "subtitle"
        elif line.endswith(".wav"):
            return "audio"
    return "audio"  # Default to audio if unsure

def convert_txt_to_json(txt_path, json_path):
    """Converts a TXT file to a JSON file based on detected format."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        format_type = detect_file_format(lines)
        result = []

        if format_type == "subtitle":
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("ID:"):
                    block, next_i = parse_subtitle_block(lines, i)
                    if block["id"]:
                        result.append(block)
                    i = next_i
                else:
                    i += 1
        else:  # audio format
            entries, _ = parse_audio_text_lines(lines, 0)
            for i, entry in enumerate(entries):
                if entry.get("wav") and (entry.get("text") or i == len(entries) - 1):  # Accept last entry even without text
                    print(f"Processing entry {i + 1}: {entry['wav']} -> {entry['text']}")
                    result.append(entry)
                else:
                    print(f"Skipping invalid entry {i + 1} in {txt_path}: {entry}")

        if not result:
            print(f"No valid entries found in {txt_path}")
        else:
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"Converted {txt_path} to {json_path} with {len(result)} entries")
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
                relative_path = os.path.relpath(root, input_dir)
                json_output_dir = os.path.join(output_dir, relative_path)
                os.makedirs(json_output_dir, exist_ok=True)
                json_file = os.path.splitext(file)[0] + '.json'
                json_path = os.path.join(json_output_dir, json_file)
                convert_txt_to_json(txt_path, json_path)

    print(f"\nConversion completed. Check {os.path.abspath(output_dir)} for .json files.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()