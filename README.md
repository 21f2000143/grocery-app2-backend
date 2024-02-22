# Steps to run this project
### First start the redis server
#### For wsl
    - sudo service redis-server start
#### For mac
    - brew services start redis
### if project not setup follow(one time script)
    - . local_setup.sh
### else just run the app
    - . local_run.sh
### To start celery workers
    - . local_workers.sh
### To run schedule tasks start celery beats
    - . local_beats.sh
