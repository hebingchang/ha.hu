import redis

socket_redis = redis.Redis(host='127.0.0.1', port=6379, db=2)

socket_redis.publish('message', '1234')
