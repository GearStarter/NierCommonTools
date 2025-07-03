import os
import json
from pathlib import Path
import string

def clean_text(text):
    """Очищает текст: удаляет пробелы, знаки пунктуации (включая японские) и приводит к нижнему регистру."""
    # Добавляем японские знаки препинания
    japanese_punctuation = "。、！？…「」『』（）［］｛｝〈〉《》【】・"
    all_punctuation = string.punctuation + japanese_punctuation
    translator = str.maketrans("", "", all_punctuation)
    return text.strip().lower().translate(translator)

def search_audio_match(phrase, audio_path):
    """Ищет фразу в JSON-файлах в audio_path, возвращает путь и wav, если найдено ровно одно совпадение."""
    matches = []
    for json_file in Path(audio_path).rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print(f"Предупреждение: Файл {json_file} не содержит список. Пропускаем.")
                continue
            
            for item in data:
                if 'text' not in item or 'wav' not in item:
                    print(f"Предупреждение: Запись в {json_file} не содержит 'text' или 'wav'. Пропускаем.")
                    continue
                if clean_text(item['text']) == clean_text(phrase):
                    # Формируем путь без audio_path
                    relative_path = os.path.relpath(json_file, audio_path).replace('\\', '/')
                    # Удаляем .json из имени файла
                    base_path = os.path.splitext(relative_path)[0]
                    # Добавляем значение wav
                    wav_path = f"{base_path}/{item['wav']}"
                    matches.append(wav_path)
        
        except Exception as e:
            print(f"Ошибка при обработке файла {json_file}: {e}")
    
    return matches

def update_json_files(text_path, audio_path):
    """Обновляет jp_voice в JSON-файлах в text_path на основе поиска в audio_path."""
    for json_file in Path(text_path).rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print(f"Предупреждение: Файл {json_file} не содержит список. Пропускаем.")
                continue

            modified = False
            for item in data:
                if 'id' not in item:
                    print(f"Предупреждение: Запись в {json_file} не содержит 'id'. Пропускаем.")
                    continue
                item_id = item['id']
                # Проверяем, пустое ли jp_voice (или отсутствует)
                if item.get('jp_voice', '') == '':
                    if 'jp' not in item:
                        print(f"Пропуск: id {item_id} в {json_file} не содержит 'jp'.")
                        continue
                    jp_phrase = item['jp']
                    # Ищем совпадения в nier_audio_json
                    matches = search_audio_match(jp_phrase, audio_path)
                    if len(matches) == 0:
                        print(f"Пропуск: Для id {item_id} в {json_file} не найдено совпадений для фразы '{jp_phrase}'.")
                    elif len(matches) > 1:
                        print(f"Пропуск: Для id {item_id} в {json_file} найдено {len(matches)} совпадений для фразы '{jp_phrase}'.")
                    else:
                        # Найдено ровно одно совпадение
                        new_jp_voice = matches[0]
                        item['jp_voice'] = new_jp_voice
                        modified = True
                        print(f"Обновлено jp_voice для id {item_id} в {json_file}: {new_jp_voice}")
                else:
                    print(f"Пропуск: jp_voice для id {item_id} в {json_file} уже заполнено.")

            # Сохраняем файл, если были изменения
            if modified:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Сохранён обновлённый файл {json_file}")
        
        except Exception as e:
            print(f"Ошибка при обработке файла {json_file}: {e}")

def main():
    # Путь к папкам (в той же директории, что и скрипт)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    text_path = os.path.join(script_dir, "nier_text_json")
    audio_path = os.path.join(script_dir, "nier_audio_json")
    
    # Проверяем существование папок
    if not os.path.exists(text_path):
        print(f"Ошибка: Папка {text_path} не найдена.")
        return
    if not os.path.exists(audio_path):
        print(f"Ошибка: Папка {audio_path} не найдена.")
        return
    
    # Запускаем обновление
    update_json_files(text_path, audio_path)

if __name__ == "__main__":
    main()