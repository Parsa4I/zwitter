# Zwitter - A Twitter-like Django Website
This is a Django website, made for learning/practice purposes. It is aimed to function somewhat like Twitter. Requirements are listed on [requirements.txt](https://github.com/Parsa4I/zwitter/blob/main/requirements.txt).

## Features
- Complete user authentication system
- Posting text/image/video
- Reposting
- Hashtags
- Trend tags
- Liking posts
- Reply
- Follow
- Profile
- Notification
- Search
- Cache (Using Redis)
- Connecting to a cloud storage for uploading media files
- Async tasks using Celery and RabbitMQ

## Setup and Usage

    # install requirements
    $ python -m venv venv
    $ pip install -r requirements.txt
Then, set up a RabbitMQ and a Redis server running on your localhost.
If you later had any connection issues between Celery and RabbitMQ,
change value of `CELERY_BROKER_URL` in `settings.py` to
`"amqp://<username>:<password>@localhost:5672/"`.
You can also change `CACHES` values,
in `settings.py`, if you have a username and
password set for your Redis server.
Just change `CAHCES["default"]["LOCATION"]`
to `"redis:///<username>:<password>@127.0.0.1:6379"`.

Create a `.env` file and write the following environment variables and place your own values:

    SECRET_KEY=django-insecure-0eg4+&h#an4l68q6do0%b_!k@0n=-^n0p+-$!it3bn&hm8ytz2
    EMAIL_HOST=<smtp host>
    EMAIL_HOST_USER=<email>
    EMAIL_HOST_PASSWORD=<email app password>
    AWS_S3_ACCESS_KEY_ID=<aws access key id>
    AWS_S3_SECRET_ACCESS_KEY=<secret access key>
    AWS_STORAGE_BUCKET_NAME=<storage bucket name>
    AWS_S3_ENDPOINT_URL=<storage endpoint url>

Run:

    $ python manage.py migrate
    $ celery -A zwitter worker -l INFO
    $ python manage.py runserver
