import os
import json
from collections import defaultdict

ROOT_DIR = "nier_text_json"
LOG_FILE = "remove_duplicates_log.txt"

def collect_json_files(root_dir):
    json_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files

def load_all_entries(json_files):
    all_entries = []
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for entry in data:
                    key = (entry.get("id"), entry.get("en"))
                    all_entries.append((key, entry, file_path))
            except json.JSONDecodeError as e:
                print(f"Ошибка JSON в файле: {file_path} — {e}")
    return all_entries

def deduplicate_entries(all_entries):
    unique_entries = {}
    duplicates_info = []

    for key, entry, file_path in all_entries:
        if key in unique_entries:
            existing = unique_entries[key]
            en_voice_before = existing["entry"].get("en_voice")
            en_voice_new = entry.get("en_voice")

            replaced_voice = False
            if (not en_voice_before) and en_voice_new:
                existing["entry"]["en_voice"] = en_voice_new
                replaced_voice = True

            duplicates_info.append({
                "id": key[0],
                "en": key[1],
                "kept_file": existing["file"],
                "duplicate_file": file_path,
                "en_voice_replaced": replaced_voice
            })
        else:
            unique_entries[key] = {"entry": entry, "file": file_path}
    return unique_entries, duplicates_info

def write_back_files(unique_entries, json_files):
    new_file_data = defaultdict(list)
    for info in unique_entries.values():
        new_file_data[info["file"]].append(info["entry"])

    for file_path in json_files:
        data = new_file_data.get(file_path, [])
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

def write_log(duplicates_info, log_file_path):
    with open(log_file_path, "w", encoding="utf-8") as log:
        for dup in duplicates_info:
            log.write(f"🔁 Повтор:\n")
            log.write(f"  ID: {dup['id']}\n")
            log.write(f"  EN: {dup['en']}\n")
            log.write(f"  ✅ Оставлен: {dup['kept_file']}\n")
            log.write(f"  ❌ Удалён:   {dup['duplicate_file']}\n")
            if dup["en_voice_replaced"]:
                log.write(f"  ⚠️  en_voice был скопирован из удалённой записи.\n")
            log.write("\n")

def main():
    print("🔍 Ищем JSON-файлы...")
    json_files = collect_json_files(ROOT_DIR)
    print(f"Найдено файлов: {len(json_files)}")

    print("📥 Загружаем данные...")
    all_entries = load_all_entries(json_files)
    print(f"Всего записей: {len(all_entries)}")

    print("🧹 Удаляем повторы...")
    unique_entries, duplicates_info = deduplicate_entries(all_entries)
    print(f"Оставлено уникальных записей: {len(unique_entries)}")
    print(f"Удалено повторов: {len(duplicates_info)}")

    print("💾 Перезаписываем JSON-файлы...")
    write_back_files(unique_entries, json_files)

    print(f"📝 Записываем лог в {LOG_FILE} ...")
    write_log(duplicates_info, LOG_FILE)

    print("✅ Готово!")

if __name__ == "__main__":
    main()
