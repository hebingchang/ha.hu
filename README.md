# ha.hu
Term Project for Web Back-End Summer Term.

## Usage
You should run redis server on port 6379

You need [pip-tools](https://github.com/nvie/pip-tools).

```
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

```
redis-server
celery --loglevel=info worker --app=hahu.celeryapp:app
python manage.py runserver

```

