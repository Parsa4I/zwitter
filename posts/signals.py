from django.dispatch import receiver
from django.db.models.signals import pre_delete
from .models import Post
from . import tasks


@receiver(pre_delete, sender=Post)
def delete_media_bucket_object(sender, instance, **kwargs):
    post_type = instance.post_type
    if post_type == "IMG":
        tasks.delete_media_bucket_object_task.delay(str(instance.image))
    elif post_type == "VID":
        tasks.delete_media_bucket_object_task.delay(str(instance.video))
