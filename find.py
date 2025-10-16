import json
import sys
from pathlib import Path


if len(sys.argv) != 2:
    print("ERROR: You must provide the instance name! Usage: python find.py <instance_name>")
    sys.exit(1)


target_name = sys.argv[1].lower()

file_path = Path("instances.json")


if not file_path.exists():
    print(f"ERROR: File {file_path} does not exist! Place it here and try again.")
    sys.exit(1)


with file_path.open(encoding="utf-8") as f:
    instances = json.load(f)

found = False

for instance in instances:
    tags = instance.get("Tags", {})
    name = tags.get("Name", "")

    if name and target_name in name.lower():
        print("SUCCESS: Matching instance found!")
        print(json.dumps(instance, indent=2, ensure_ascii=False))
        found = True
        break

if not found:
    print(f"WARNING: No instances found with Name containing '{target_name}'!")
