import os
import json

def list_directory(path, indent="", structure=None):
    if structure is None:
        structure = {"path": path, "contents": []}
    
    try:
        # Получаем отсортированный список элементов в директории
        items = sorted(os.listdir(path))
        
        for item in items:
            item_path = os.path.join(path, item)
            item_info = {"name": item}
            
            if os.path.isdir(item_path):
                item_info["type"] = "directory"
                item_info["contents"] = []
                print(f"{indent}📁 {item}/")
                list_directory(item_path, indent + "  ", item_info)
            else:
                item_info["type"] = "file"
                print(f"{indent}📄 {item}")
            
            structure["contents"].append(item_info)
                    
    except PermissionError:
        print(f"{indent}⚠️ Нет доступа: {path}")
    except Exception as e:
        print(f"{indent}❌ Ошибка при обработке {path}: {str(e)}")
    
    return structure

def main():
    # Запрашиваем путь к директории
    directory = input("Введите путь к директории (или нажмите Enter для текущей): ").strip()
    if not directory:
        directory = os.getcwd()
    
    # Проверяем существование директории
    if not os.path.exists(directory):
        print(f"❌ Директория {directory} не существует")
        return
    
    # Собираем структуру директории
    print(f"\nСодержимое директории: {directory}\n")
    structure = list_directory(directory)
    
    # Сохраняем результат в JSON
    output_path = "directory_list.json"
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(structure, output_file, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Список сохранен в {output_path}")

if __name__ == "__main__":
    main()