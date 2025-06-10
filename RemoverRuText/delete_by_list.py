import os
import json
import shutil

def delete_items(base_path, structure):
    try:
        # Получаем список элементов из JSON
        items = {item["name"]: item for item in structure["contents"]}
        
        # Проходим по содержимому текущей директории
        for item_name in os.listdir(base_path):
            item_path = os.path.join(base_path, item_name)
            
            # Проверяем, есть ли элемент в списке
            if item_name not in items:
                print(f"⏩ Пропущен (не в списке): {item_path}")
                continue
            
            item_info = items[item_name]
            
            if item_info["type"] == "directory":
                # Рекурсивно обрабатываем поддиректорию
                print(f"📁 Обрабатывается директория: {item_path}")
                delete_items(item_path, item_info)
                # Проверяем, пуста ли директория
                if not os.listdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
                    print(f"🗑️ Удалена директория: {item_path}")
                else:
                    print(f"⚠️ Директория не пуста, пропущена: {item_path}")
            else:
                # Удаляем файл
                try:
                    os.remove(item_path)
                    print(f"🗑️ Удален файл: {item_path}")
                except Exception as e:
                    print(f"❌ Ошибка при удалении файла {item_path}: {str(e)}")
                    
    except PermissionError:
        print(f"⚠️ Нет доступа: {base_path}")
    except Exception as e:
        print(f"❌ Ошибка при обработке {base_path}: {str(e)}")

def main():
    json_path = "directory_list.json"
    
    # Проверяем существование JSON-файла
    if not os.path.exists(json_path):
        print(f"❌ Файл списка {json_path} не найден")
        return
    
    # Читаем JSON
    with open(json_path, "r", encoding="utf-8") as file:
        structure = json.load(file)
    
    # Используем текущую директорию как базовую
    base_path = os.getcwd()
    
    print(f"\nУдаление элементов в: {base_path}\n")
    delete_items(base_path, structure)
    print("\n✅ Удаление завершено")
    
    # Ожидаем ввода пользователя перед закрытием
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()