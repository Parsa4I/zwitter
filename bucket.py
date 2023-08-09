import boto3
from django.conf import settings


class Bucket:
    def __init__(self):
        try:
            self.s3 = boto3.resource(
                service_name="s3",
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
            )
        except Exception as exc:
            print(exc)

    def buckets_list(self):
        for buc in self.s3.buckets.all():
            yield buc.name

    def get_objs(self):
        bucket = self.s3.Bucket(name=settings.AWS_STORAGE_BUCKET_NAME)
        return bucket.objects.all()

    def delete_obj(self, key):
        return self.s3.Object(settings.AWS_STORAGE_BUCKET_NAME, key).delete()

    def download_obj(self, key):
        return self.s3.Object(settings.AWS_STORAGE_BUCKET_NAME, key).download_file(
            f"{settings.BASE_DIR}/aws/{key}"
        )


bucket = Bucket()
