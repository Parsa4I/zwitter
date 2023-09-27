from django.db import models
from django.db.models import Q


class ProductQuerySet(models.QuerySet):
    def search(self, q):
        qs = self.filter(Q(body__icontains=q) | Q(tags__title__icontains=q))
        return qs


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def search(self, q):
        return self.get_queryset().search(q)
