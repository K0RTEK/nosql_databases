# Итоговое задание по модулю 3 - MongoDB (университет)

Проект выполняет требования задания:
- проектирование БД студентов университета;
- реализация шардинга;
- простой Python-интерфейс;
- нагрузочное тестирование;
- подготовка отчёта.

## 1. Структура проекта

```text
mongo_university_project/
├─ app/
│  ├─ cli.py
│  └─ db.py
├─ data/
│  └─ generate_sample_data.py
├─ report/
│  └─ report_template.md
├─ schemas/
│  ├─ assignments.schema.json
│  ├─ attendances.schema.json
│  ├─ courses.schema.json
│  ├─ grades.schema.json
│  ├─ students.schema.json
│  └─ submissions.schema.json
├─ scripts/
│  ├─ create_collections.py
│  ├─ create_indexes.py
│  ├─ enable_sharding.js
│  ├─ init_single_node_rs.js
│  └─ seed_data.py
├─ tests/
│  └─ load_test.py
├─ .env.example
├─ requirements.txt
└─ README.md
```

## 2. Почему в проекте есть исправления схем

Исходные JSON-схемы требуют небольшого исправления:
- `students.json`: поле `university_course_id` есть в `required`, но отсутствует в `properties`.
- `assignments.json`: отсутствует `assignment_id`, хотя коллекция `submissions` содержит ссылку на него.

В рабочей реализации эти поля добавлены, чтобы модель данных была согласованной.

## 3. Логика модели данных

Коллекции:
- `students` - студенты;
- `courses` - курсы;
- `assignments` - задания;
- `submissions` - сдачи заданий;
- `grades` - оценки;
- `attendances` - посещаемость.

### Основные связи
- один курс -> много студентов;
- один курс -> много заданий;
- студент сдаёт много заданий;
- студент получает много оценок;
- студент имеет много записей посещаемости.

## 4. Выбор ключа шардирования

Основной шардируемой коллекцией выбрана `submissions`.

Предлагаемый shard key:
```javascript
{ course_id: 1, student_id: 1, assignment_id: 1 }
```

### Обоснование
- нагрузка чаще всего возникает на массовых операциях по сдачам;
- запросы преподавателя обычно фильтруются по курсу;
- внутри курса есть распределение по студентам и заданиям;
- составной ключ уменьшает риск дисбаланса по сравнению с одним `course_id`.

Дополнительно можно шардировать `attendances` по:
```javascript
{ course_id: 1, student_id: 1, date: 1 }
```

## 5. Как запустить на текущем standalone MongoDB

Если у тебя сейчас просто один контейнер MongoDB, проект всё равно можно частично проверить:

1. Установить зависимости:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Скопировать `.env.example` в `.env` и оставить свой URI.

3. Создать коллекции и индексы:
```bash
python scripts/create_collections.py
python scripts/create_indexes.py
```

4. Сгенерировать и загрузить тестовые данные:
```bash
python scripts/seed_data.py --students 1000 --courses 20 --assignments 100
```

5. Запустить интерфейс:
```bash
python app/cli.py
```

6. Запустить нагрузочное тестирование:
```bash
python tests/load_test.py --operations 3000 --workers 20
```

## 6. Как реализовать шардинг

Для высокой оценки лучше использовать отдельный кластер с `mongos`, `config server` и минимум двумя shard replica set.

### Минимальный сценарий
1. Поднять config server replica set.
2. Поднять 2 shard replica set.
3. Поднять `mongos`.
4. Выполнить:
```javascript
sh.enableSharding('university_db')
sh.shardCollection('university_db.submissions', { course_id: 1, student_id: 1, assignment_id: 1 })
sh.shardCollection('university_db.attendances', { course_id: 1, student_id: 1, date: 1 })
```


## 6A. Готовый вариант sharded-кластера в Docker

В проект добавлен файл `docker-compose.sharded.yml` и скрипт `scripts/init_sharded_cluster.sh`.

### Запуск
```bash
docker compose -f docker-compose.sharded.yml up -d
bash scripts/init_sharded_cluster.sh
```

После этого подключаться к приложению нужно через `mongos`, например:
```env
MONGO_URI=mongodb://localhost:27017/
APP_DB=university_db
```

Далее:
```bash
python scripts/create_collections.py
python scripts/create_indexes.py
python scripts/seed_data.py --students 1000 --courses 20 --assignments 100
mongosh localhost:27017 scripts/enable_sharding.js
```

## 7. Полезные команды для проверки

Проверить шардирование:
```javascript
sh.status()
```

Проверить распределение чанков:
```javascript
db.submissions.getShardDistribution()
```

Посмотреть валидаторы:
```javascript
db.getCollectionInfos({name: 'students'})
```

## 8. Что вставить в отчёт

Основа для отчёта лежит в файле:
- `report/report_template.md`

Туда останется добавить:
- скриншоты `sh.status()`;
- скриншоты работы CLI;
- результаты `load_test.py` и построенный график.

