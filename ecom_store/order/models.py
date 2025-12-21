from config.models import BaseModel
from django.db import models


# Create your models here.
class Courier(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.code}"