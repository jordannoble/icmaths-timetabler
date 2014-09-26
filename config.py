import os, redis
from timetabler import app

env = os.getenv('ENV', 'DEV')

app.debug = True
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

if env == 'PROD':
  app.debug = False

