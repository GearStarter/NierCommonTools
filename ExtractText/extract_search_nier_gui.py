import os
import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QFileDialog, 
                            QTextEdit, QLabel)
from PyQt6.QtCore import Qt
import string

class SearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Search Tool")
        self.setGeometry(100, 100, 600, 400)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Folder: Not selected")
        self.choose_button = QPushButton("Choose Folder")
        self.choose_button.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.choose_button)
        layout.addLayout(folder_layout)

        # Phrase input
        phrase_layout = QHBoxLayout()
        self.phrase_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search)
        phrase_layout.addWidget(QLabel("Phrase:"))
        phrase_layout.addWidget(self.phrase_input)
        phrase_layout.addWidget(self.search_button)
        layout.addLayout(phrase_layout)

        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

        self.folder_path = ""

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f"Folder: {folder}")

    def search_phrase(self, phrase):
        """Searches for a phrase in JSON files, ignoring case and punctuation, and returns full subtitle blocks."""
        found = False
        results = []
        translator = str.maketrans("", "", string.punctuation)
        clean_phrase = phrase.lower().translate(translator)

        for root, _, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            subtitles = json.load(f)
                            for idx, subtitle in enumerate(subtitles):
                                for key in ['id', 'jp', 'en', 'ru']:
                                    value = subtitle.get(key, "")
                                    clean_value = value.lower().translate(translator)
                                    if clean_phrase in clean_value:
                                        if not found:
                                            found = True
                                        result = f"File: {file_path}\n"
                                        result += f"ID: {subtitle.get('id', '')}\n"
                                        result += f"JP: {subtitle.get('jp', '')}\n"
                                        result += f"EN: {subtitle.get('en', '')}\n"
                                        result += f"RU: {subtitle.get('ru', '')}\n"
                                        result += f"{'-' * 50}\n"
                                        results.append(result)
                    except Exception as e:
                        results.append(f"Error reading {file_path}: {str(e)}\n")
        
        if not found and not any("Error" in r for r in results):
            results.append(f"\nPhrase '{phrase}' not found in text files.\n")
        
        return results

    def search(self):
        phrase = self.phrase_input.text().strip()
        if not phrase:
            self.results_text.setText("Please enter a phrase to search.")
            return
        if not self.folder_path:
            self.results_text.setText("Please select a folder first.")
            return

        self.results_text.clear()
        translator = str.maketrans("", "", string.punctuation)
        clean_phrase = phrase.lower().translate(translator)
        if not clean_phrase:
            self.results_text.setText("Phrase contains only punctuation. Please enter a valid phrase.")
            return

        results = self.search_phrase(clean_phrase)
        self.results_text.setText("".join(results))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchWindow()
    window.show()
    sys.exit(app.exec())