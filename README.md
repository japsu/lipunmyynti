== Getting started ==

    apt-get install nodejs
    npm install -g stylus

    virtualenv --distribute --no-site-packages venv-lipunmyynti
    source venv-lipunmyynti/bin/activate

    git clone /srv/git/lipunmyynti.git
    cd lipunmyynti

    pip install -r requirements.txt
    pip install psycopg2 # for production only

    python manage.py syncdb
    python manage.py migrate
    python manage.py run_gunicorn 127.0.0.1:9001
    iexplore http://127.0.0.1:9001
