exec gunicorn --workers 4 -b unix:/socket/ftown.sock -m 777 manage:app
