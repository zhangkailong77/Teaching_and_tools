from app.core.redis import redis_client
print('Redis ping:', redis_client.ping())
redis_client.set('test_connection', 'hello')
print('Write test: OK')
print('Read test:', redis_client.get('test_connection'))
