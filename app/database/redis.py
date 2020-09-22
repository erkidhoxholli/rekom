from redis import StrictRedis, ConnectionError

redis_client = StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

def is_connected():
    try:
        redis_client.ping()
        return True
    except ConnectionError:
        print(f'Error connecting to redis. Exiting...')
        return False
