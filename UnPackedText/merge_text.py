import os
import shutil

def parse_text_file(file_path):
    """Parses a text file and returns a dictionary with ID and corresponding lines."""
    result = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            current_id = None
            for line in f:
                line = line.strip()
                if line.startswith('ID:'):
                    current_id = line
                    result[current_id] = {'JP': '', 'EN': '', 'RU': ''}
                elif line.startswith('JP:') and current_id:
                    result[current_id]['JP'] = line
                elif line.startswith('EN:') and current_id:
                    result[current_id]['EN'] = line
                elif line.startswith('RU:') and current_id:
                    result[current_id]['RU'] = line
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}")
    return result

def merge_texts(source_dir, ru_dir, result_dir):
    """Merges text files by copying source files and adding RU text from RU files."""
    # Copy all contents from source_dir to result_dir
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    shutil.copytree(source_dir, result_dir)

    # Process each file in result_dir
    for root, _, files in os.walk(result_dir):
        for file in files:
            if file.endswith('.txt'):
                result_path = os.path.join(root, file)
                # Calculate relative path to find corresponding RU file
                relative_path = os.path.relpath(result_path, result_dir)
                ru_path = os.path.join(ru_dir, relative_path)

                # Parse source (result) file
                result_data = parse_text_file(result_path)

                # Parse RU file if it exists
                ru_data = {}
                if os.path.exists(ru_path):
                    ru_data = parse_text_file(ru_path)
                else:
                    print(f"Warning: No matching RU file found for {result_path}")

                # Update RU in result file
                try:
                    with open(result_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    with open(result_path, 'w', encoding='utf-8') as f:
                        current_id = None
                        for line in lines:
                            line = line.strip()
                            if line.startswith('ID:'):
                                current_id = line
                                f.write(f"{line}\n")
                            elif line.startswith('JP:') and current_id:
                                f.write(f"{line}\n")
                            elif line.startswith('EN:') and current_id:
                                f.write(f"{line}\n")
                            elif line.startswith('RU:') and current_id:
                                ru_text = ru_data.get(current_id, {}).get('EN', '')
                                if ru_text:
                                    f.write(f"RU: {ru_text[4:]}\n")  # Remove 'EN: ' prefix
                                else:
                                    f.write(f"{line}\n")  # Keep original RU if no match
                            else:
                                f.write(f"{line}\n")
                except Exception as e:
                    print(f"Error updating {result_path}: {str(e)}")

def main():
    # Define directory paths
    source_dir = "nier_unpacked_extracted"
    ru_dir = "nier_unpacked_extracted_ru"
    result_dir = "nier_unpacked_extracted_result"

    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Error: {source_dir} not found.")
        return
    if not os.path.exists(ru_dir):
        print(f"Warning: {ru_dir} not found, proceeding with only source data.")
        ru_dir = None

    # Perform merge
    merge_texts(source_dir, ru_dir, result_dir)
    print(f"\nMerging completed. Results saved to {os.path.abspath(result_dir)}")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()