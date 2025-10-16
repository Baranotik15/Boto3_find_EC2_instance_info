import json
import sys
from pathlib import Path


if len(sys.argv) != 2:
    print("Используйте в терминале: python find.py <имя_инстанса>")
    sys.exit(1)


target_name = sys.argv[1].lower()

file_path = Path("instances.json")


if not file_path.exists():
    print(f"Файл {file_path} не найден")
    sys.exit(1)


with file_path.open(encoding="utf-8") as f:
    instances = json.load(f)

found = False
for instance in instances:
    tags = instance.get("Tags", {})
    name = tags.get("Name", "")

    if name and target_name in name.lower():
        print("Данные найдены:")
        print(json.dumps(instance, indent=2, ensure_ascii=False))
        found = True
        break

if not found:
    print(f"Данные с Name, содержащим '{target_name}', не найден")

