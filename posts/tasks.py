from celery import shared_task
from bucket import bucket


@shared_task
def delete_media_bucket_object_task(key):
    return bucket.delete_obj(key)
