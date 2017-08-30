#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

''' Automatic deployment script '''
import time
from fabric.api import env, run, cd, prefix
import os

if os.path.exists('.env'):
    print('import env from local')
    with open('.env') as f:
        for l in f:
            key, value = l.strip().split('=')
            os.environ[key] = value


env.host_string = os.getenv('DEPLOY_HOSTS')


def deploy():
    with cd('/srv/Ftown'):
        with prefix('source ftownvenv/bin/activate'):
            run('git fetch --all')
            run('git reset --hard origin/master')
            run('supervisorctl -c ./supervisord.conf stop ftown')
            run('./manage.py db migrate')
            time.sleep(5)
            run('./manage.py db upgrade')
            time.sleep(6)
            run('supervisorctl -c ./supervisord.conf start ftown')
