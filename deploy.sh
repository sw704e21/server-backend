#!/bin/bash

cd "/var/www/cryptoserver/server-backend/" || exit

git pull

cd ..

docker kill server-backend

docker rm server-backend

docker image build -t server-backend -f server-backend/Dockerfile server-backend

docker run -d -p 65432:65432 -v backend:/logs --name server-backend server-backend