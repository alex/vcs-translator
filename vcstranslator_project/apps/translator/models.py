from django.db import models


class BaseFeedback(models.Model):
    source = models.CharField(max_length=30)
    target = models.CharField(max_length=30)
    command = models.TextField()

    class Meta:
        abstract = False

class FailedTranslation(BaseFeedback):
    count = models.IntegerField(default=0)
