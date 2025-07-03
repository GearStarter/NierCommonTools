import os
import json
from pathlib import Path
import pandas as pd

def load_excel_data(excel_file):
    """Читает Excel-файл с построчной структурой (столбец A: ключи, столбец B: значения) и возвращает словарь {sheet_name: {id: en_voice}}."""
    try:
        xl = pd.ExcelFile(excel_file)
        excel_data = {}
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
            id_to_en_voice = {}
            current_id = None
            current_record = {}
            
            # Обрабатываем строки
            for index, row in df.iterrows():
                key = str(row[0]).strip() if pd.notna(row[0]) else ""
                value = str(row[1]).strip() if pd.notna(row[1]) else ""
                
                if key == "id":
                    if current_id and current_record.get("en_voice"):
                        id_to_en_voice[current_id] = current_record["en_voice"]
                    current_id = value
                    current_record = {"id": value}
                elif key in ["jp", "en", "ru", "en_voice", "jp_voice"]:
                    current_record[key] = value
            
            # Добавляем последнюю запись, если en_voice не пустое
            if current_id and current_record.get("en_voice"):
                id_to_en_voice[current_id] = current_record["en_voice"]
            
            if id_to_en_voice:
                excel_data[sheet_name] = id_to_en_voice
            else:
                print(f"Предупреждение: Лист {sheet_name} не содержит записей с непустым en_voice.")
        
        return excel_data
    except Exception as e:
        print(f"Ошибка при чтении Excel-файла {excel_file}: {e}")
        return {}

def update_json_files(excel_file, base_path):
    """Обновляет JSON-файлы в base_path на основе данных из Excel."""
    # Загружаем данные из Excel
    excel_data = load_excel_data(excel_file)
    if not excel_data:
        print("Не удалось загрузить данные из Excel. Прерываем выполнение.")
        return

    # Обходим все подпапки (core, ph1, ph2 и т.д.)
    for folder in Path(base_path).iterdir():
        if not folder.is_dir():
            continue
        folder_name = folder.name
        # Проверяем, есть ли соответствующий лист в Excel
        if folder_name not in excel_data:
            print(f"Предупреждение: Лист {folder_name} не найден в Excel. Пропускаем папку {folder}.")
            continue

        # Получаем словарь {id: en_voice} для текущего листа
        id_to_en_voice = excel_data[folder_name]

        # Обходим все JSON-файлы в папке (включая подпапки)
        for json_file in folder.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    print(f"Предупреждение: Файл {json_file} не содержит список. Пропускаем.")
                    continue

                modified = False
                # Обновляем каждую запись
                for item in data:
                    if 'id' not in item:
                        print(f"Предупреждение: Запись в {json_file} не содержит 'id'. Пропускаем.")
                        continue
                    item_id = item['id']
                    # Проверяем, пустое ли en_voice (или отсутствует)
                    if item.get('en_voice', '') == '':
                        # Ищем id в таблице
                        if item_id in id_to_en_voice:
                            new_en_voice = id_to_en_voice[item_id]
                            if new_en_voice:  # Убедимся, что en_voice не пустое
                                item['en_voice'] = new_en_voice
                                modified = True
                                print(f"Обновлено en_voice для id {item_id} в {json_file}: {new_en_voice}")
                            else:
                                print(f"Пропуск: en_voice для id {item_id} в таблице пустое.")
                        else:
                            print(f"Пропуск: id {item_id} не найден в листе {folder_name}.")
                    else:
                        print(f"Пропуск: en_voice для id {item_id} в {json_file} уже заполнено.")

                # Сохраняем файл, если были изменения
                if modified:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"Сохранён обновлённый файл {json_file}")
            
            except Exception as e:
                print(f"Ошибка при обработке файла {json_file}: {e}")

def main():
    # Путь к Excel-файлу (в той же директории, что и скрипт)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(script_dir, "nier_subtitles.xlsx")
    # Путь к папке с JSON-файлами
    base_path = os.path.join(script_dir, "nier_text_json")
    
    # Проверяем существование Excel-файла
    if not os.path.exists(excel_file):
        print(f"Ошибка: Excel-файл {excel_file} не найден.")
        return
    
    # Проверяем существование папки nier_text_json
    if not os.path.exists(base_path):
        print(f"Ошибка: Папка {base_path} не найдена.")
        return
    
    # Запускаем обновление
    update_json_files(excel_file, base_path)

if __name__ == "__main__":
    main()