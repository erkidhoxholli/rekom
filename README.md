> TODO:
* WIP: Use docker: https://fastapi.tiangolo.com/deployment/
* Error handling for redis
* Setup Lets encrypt
* use https://redis.io/topics/transactions instead of using intermediate results and deleting them afterwards
* Setup neptune.ai to keep track of experiments

## docker setup
docker build -t rekom .
docker run -d --name rekom_api -p 80:3000 rekom

