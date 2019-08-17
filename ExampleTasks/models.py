from django.db import models

# Create your models here.

class Task(models.Model):

    task_id = models.CharField(max_length=500, null=False, blank=False)
    task_type = models.CharField(max_length=100)


class CSVData(models.Model):

    task_id = models.ForeignKey(Task, on_delete=models.CASCADE)
    data = models.CharField(max_length=1000, null=True, blank=True)