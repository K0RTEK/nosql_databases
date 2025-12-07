from pymongo import MongoClient
from DML import MongoDML
from data_generator import DataGenerator
from queries import UniversityQueries


def main():
    dml.drop_collections()
    dml.create_collections()

    data_generator.generate_all()
    queries.get_all_queries_result()


if __name__ == '__main__':
    db = 'university'

    client = MongoClient('localhost', 27017, username='kirill', password='5567')

    dml = MongoDML(
        client=client,
        db=db,
        schemas_folder_path='./schemas/',
    )

    data_generator = DataGenerator(
        client=client,
        db=db
    )

    queries = UniversityQueries(
        client=client,
        db=db
    )

    main()
