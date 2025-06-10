import os
import time

def search_phrase(phrase):
    """Searches for a phrase in text files in the current directory and its subdirectories, ignoring case."""
    found = False
    results = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_number, line in enumerate(f, 1):
                            if phrase.lower() in line.lower():
                                if not found:
                                    found = True
                                result = f"File: {file_path}\nLine {line_number}: {line.strip()}\n{'-' * 50}\n"
                                print(result.strip())
                                results.append(result)
                except Exception as e:
                    print(f"Error reading {file_path}: {str(e)}")
    
    if not found:
        print(f"\nPhrase '{phrase}' not found in text files.")
        results.append(f"Phrase '{phrase}' not found in text files.\n")
    
    return results

def save_results(results):
    """Saves search results to a text file, overwriting existing content with a timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    filename = "search_results.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"--- Search Results - {timestamp} ---\n")
        f.writelines(results)

def main():
    # Prompt user for a phrase
    phrase = input("Enter a phrase to search (or press Enter to exit): ").strip()
    if not phrase:
        print("Search canceled.")
        return
    
    # Perform search in the current directory
    results = search_phrase(phrase)
    
    # Save results to file
    if results:
        save_results(results)
        print(f"\nResults saved to {os.path.abspath('search_results.txt')}")
    
    # Wait for input before closing
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()