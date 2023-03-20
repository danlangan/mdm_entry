from django.db import models

# Create your models here.

class DataSource(models.Model):
    data_source = models.CharField(max_length=255)