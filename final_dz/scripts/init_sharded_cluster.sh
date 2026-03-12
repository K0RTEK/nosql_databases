#!/usr/bin/env bash
set -e

echo "Initializing config replica set..."
docker exec configsvr mongosh --port 27019 --eval '
rs.initiate({_id:"cfgReplSet",configsvr:true,members:[{_id:0,host:"configsvr:27019"}]})
'

echo "Initializing shard1 replica set..."
docker exec shard1 mongosh --port 27018 --eval '
rs.initiate({_id:"shard1ReplSet",members:[{_id:0,host:"shard1:27018"}]})
'

echo "Initializing shard2 replica set..."
docker exec shard2 mongosh --port 27028 --eval '
rs.initiate({_id:"shard2ReplSet",members:[{_id:0,host:"shard2:27028"}]})
'

sleep 10

echo "Adding shards to mongos..."
docker exec mongos mongosh --port 27017 --eval '
sh.addShard("shard1ReplSet/shard1:27018");
sh.addShard("shard2ReplSet/shard2:27028");
sh.status();
'

echo "Cluster initialized."
