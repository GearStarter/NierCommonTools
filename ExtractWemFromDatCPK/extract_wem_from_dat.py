import os
import struct

def find_riff_signature(file_data, start_pos=0):
    """Finds the RIFF signature in binary data."""
    riff_signature = b'RIFF'
    wave_signature = b'WAVEfmt '
    while start_pos < len(file_data) - 12:
        if file_data[start_pos:start_pos + 4] == riff_signature:
            if file_data[start_pos + 8:start_pos + 16] == wave_signature:
                return start_pos
        start_pos += 1
    return -1

def extract_wem_file(file_path, output_base_dir):
    """Extracts WEM files from a file based on RIFF signature."""
    file_name = os.path.basename(file_path)
    output_dir = os.path.join(output_base_dir, file_name)
    wem_extracted = False

    with open(file_path, 'rb') as f:
        file_data = f.read()

    pos = 0
    file_count = 0
    while True:
        pos = find_riff_signature(file_data, pos)
        if pos == -1:
            break

        # Read chunk size (4 bytes after RIFF)
        chunk_size = struct.unpack('<I', file_data[pos + 4:pos + 8])[0]
        end_pos = pos + 8 + chunk_size

        if end_pos > len(file_data):
            print(f"Warning: Chunk size exceeds file length in {file_path} at pos {pos}, adjusting to end.")
            end_pos = len(file_data)

        # Extract the chunk
        wem_data = file_data[pos:end_pos]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, f"{file_count}.wem")
        with open(output_file, 'wb') as out_f:
            out_f.write(wem_data)

        print(f"Extracted {output_file} (size: {len(wem_data)} bytes)")
        file_count += 1
        pos = end_pos
        wem_extracted = True

    # Remove directory if no WEM files were extracted
    if not wem_extracted and os.path.exists(output_dir):
        shutil.rmtree(output_dir)

def main():
    # Define input and output directories
    input_dir = "nier_unpacked"
    output_dir = "nier_unpacked_result"

    if not os.path.exists(input_dir):
        print(f"Error: {input_dir} not found.")
        return

    # Process all files in input directory
    for root, _, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, input_dir)
            output_base_dir = os.path.join(output_dir, relative_path)

            print(f"Processing {file_path}")
            extract_wem_file(file_path, output_base_dir)

    print(f"\nExtraction completed. Check {os.path.abspath(output_dir)} for .wem files.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    import shutil  # Added for rmtree
    main()