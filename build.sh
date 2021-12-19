#!/usr/bin/env bash
git pull origin master
rm -r ./target
mkdir -p ./target/minions.feeder
mkdir -p ./target/minions.common

mkdir -p ./target/phantomjs-2.1.1-linux-x86_64

cp -r ./config                          ./target/minions.feeder
cp -r ./minions_feeder                  ./target/minions.feeder
cp app.py                               ./target/minions.feeder

cp -r ../minions.common/minions_common  ./target/minions.common
cp -r ../minions.common/thrift          ./target/minions.common
cp -r ../minions.common/config          ./target/minions.common

cp -r "/mnt/d/Program Files/phantomjs-2.1.1-linux-x86_64" ./target

cp Requirements.txt                     ./target
cp Dockerfile                           ./target

mkdir -p ./../minions.environment/runtime/minions.feeder/config
cp ./config/* ./../minions.environment/runtime/minions.feeder/config

docker build -t 192.168.1.202:5000/feeder:1.0 ./target
docker push 192.168.1.202:5000/feeder:1.0