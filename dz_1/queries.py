from urllib.parse import quote_plus as quote
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

objects_in_london = 0
price_above_200 = 0
min_price_object = None
objects_in_cities = {}
most_reviewed_object = None

for doc in collection.find():
    curr_price = float(doc['price'].get('$numberDecimal'))
    curr_reviews = int(doc['number_of_reviews'].get('$numberInt'))
    city = doc['address']['market']

    # Найти количество объектов, находящихся в Лондоне.
    if city == 'London':
        objects_in_london += 1

    # Найти количество объектов с ценой выше $200.
    if curr_price > 200:
        price_above_200 += 1

    # Найти объект с минимальной ценой.
    if min_price_object is None:
        min_price_object = doc
    else:
        min_price = float(min_price_object['price'].get('$numberDecimal'))
        if curr_price < min_price:
            min_price_object = doc

    # Найти город с максимальным количеством объектов.
    objects_in_cities[city] = objects_in_cities.get(city, 0) + 1

    # Найти объект с наибольшим количеством отзывов и вывести его название и количество отзывов.
    if most_reviewed_object is None:
        most_reviewed_object = doc
    else:
        max_reviews = int(most_reviewed_object['number_of_reviews'].get('$numberInt'))
        if curr_reviews > max_reviews:
            most_reviewed_object = doc

print("Количество объектов, находящихся в Лондоне: ", objects_in_london)
print("Количество объектов с ценой выше $200: ", price_above_200)
print("Объект с минимальной ценой: ", min_price_object)
print("Город с максимальным количеством объектов: ", max(objects_in_cities, key=objects_in_cities.get))
print("Объект с наибольшим количеством отзывов: ", f"Имя: {most_reviewed_object.get('name')}, Кол-во отзывов: {int(most_reviewed_object['number_of_reviews'].get('$numberInt'))}")