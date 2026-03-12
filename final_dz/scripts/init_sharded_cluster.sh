#!/usr/bin/env bash
set -e

echo "Инициализация конфигурационного набора реплик..."
docker exec configsvr mongosh --port 27019 --eval '
rs.initiate({
  _id: "cfgReplSet",
  configsvr: true,
  members: [{ _id: 0, host: "configsvr:27019" }]
})
'

echo "Инициализация набора реплик shard1..."
docker exec shard1 mongosh --port 27018 --eval '
rs.initiate({
  _id: "shard1ReplSet",
  members: [{ _id: 0, host: "shard1:27018" }]
})
'

echo "Инициализация набора реплик shard2..."
docker exec shard2 mongosh --port 27028 --eval '
rs.initiate({
  _id: "shard2ReplSet",
  members: [{ _id: 0, host: "shard2:27028" }]
})
'

echo "Ожидание запуска наборов реплик..."
sleep 10

echo "Добавление шардов и включение шардинга..."
docker exec mongos mongosh --port 27017 --eval '
sh.addShard("shard1ReplSet/shard1:27018");
sh.addShard("shard2ReplSet/shard2:27028");
sh.enableSharding("university_db");
sh.shardCollection("university_db.submissions", { course_id: 1, student_id: 1, assignment_id: 1 });
sh.shardCollection("university_db.attendances", { course_id: 1, student_id: 1, date: 1 });
sh.status();
'

echo "Кластер успешно инициализирован"