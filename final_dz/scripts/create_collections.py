import json
from pathlib import Path
from pymongo.errors import CollectionInvalid
from app.db import get_db

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def main():
    db = get_db()
    mapping = {
        "students": "students.schema.json",
        "courses": "courses.schema.json",
        "assignments": "assignments.schema.json",
        "submissions": "submissions.schema.json",
        "grades": "grades.schema.json",
        "attendances": "attendances.schema.json",
    }

    for collection_name, file_name in mapping.items():
        schema = json.loads((SCHEMA_DIR / file_name).read_text(encoding="utf-8"))
        try:
            db.create_collection(
                collection_name,
                validator=schema,
                validationLevel="strict",
                validationAction="error",
            )
            print(f"[OK] создана коллекция {collection_name}")
        except CollectionInvalid:
            print(f"[SKIP] {collection_name} уже существует")
            db.command({
                "collMod": collection_name,
                "validator": schema,
                "validationLevel": "strict",
                "validationAction": "error",
            })
            print(f"[OK] обновлен валидатор для {collection_name}")


if __name__ == "__main__":
    main()
