import os
import json
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid


class MongoDML:
    def __init__(self, client, db: str, schemas_folder_path: str):
        self.client = client
        self.db = self.client[db]
        self.schemas_folder_path = schemas_folder_path

    def drop_collections(self):
        print("=" * 27)
        print("——>", "Удаление коллекций", "<———")
        print("=" * 27)
        if not os.listdir(self.schemas_folder_path):
            raise FileNotFoundError("Директория с схемами коллекций пустая")
        elif not list(self.db.list_collection_names()):
            print("Коллекции отсутствуют")
        else:
            for schema_file in os.listdir(self.schemas_folder_path):
                collection_name = schema_file.split('.')[0]
                collection = self.db[collection_name]
                collection.drop()
                print(f"\tКоллекция {collection_name} удалена")

        print("\n")

    def create_collections(self):
        print("=" * 27)
        print("——>", "Создание коллекций", "<———")
        print("=" * 27)
        if not os.listdir(self.schemas_folder_path):
            raise FileNotFoundError("Директория с схемами коллекций пустая")
        else:
            for schema_file in os.listdir(self.schemas_folder_path):
                collection_name = schema_file.split('.')[0]

                with open(self.schemas_folder_path + schema_file) as f:
                    schema = json.load(f)

                try:
                    self.db.create_collection(
                        collection_name,
                        validator=schema,
                        validationLevel="strict",
                        validationAction="error"
                    )
                    print(f"\tКоллекция {collection_name} создана")
                except CollectionInvalid:
                    print(f"\tКоллекция {collection_name} уже существует")

        print("\n")


if __name__ == '__main__':
    client = MongoClient('localhost', 27017, username='kirill', password='5567')

    dml = MongoDML(
        client=client,
        db='university',
        schemas_folder_path='./schemas/'
    )

    dml.drop_collections()
    dml.create_collections()
