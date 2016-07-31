DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hahu',
        'HOST': 'database',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET foreign_key_checks = 0;',
        },
    }
}

REDIS_HOST = 'redis'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# celery

BROKER_URL = 'redis://redis/0'
CELERY_RESULT_BACKEND = 'redis://redis/0'
