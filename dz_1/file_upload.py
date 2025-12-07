from urllib.parse import quote_plus as quote

import json
import pymongo

url = 'mongodb://{user}:{pw}@{hosts}/?replicaSet={rs}&authSource={auth_src}'.format(
    user=quote('user1'),
    pw=quote('9181287qQq;!@#$'),
    hosts=','.join([
        'rc1b-pbdfa7cajffsgbdp.mdb.yandexcloud.net:27018','rc1b-pbdfa7cajffsgbdp.mdb.yandexcloud.net:27018'
    ]),
    rs='rs01',
    auth_src='db1')
dbs = pymongo.MongoClient(
    url,
    tls=True,
    tlsCAFile='/Users/kirill/.mongodb/root.crt')['db1']

db = dbs['db1']
collection = db['collection1']

documents = []
with open('listingsAndReviews.json', 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue  # пропускаем пустые строки
        try:
            doc = json.loads(line)
            documents.append(doc)
        except json.JSONDecodeError as e:
            print(f"Ошибка в строке {line_num}: {e}")
            print(f"Содержимое строки: {line[:100]}...")
            raise

if documents:
    result = collection.insert_many(documents, ordered=False)
    print(f"Успешно вставлено {len(result.inserted_ids)} документов.")
else:
    print("Нет данных для вставки.")


