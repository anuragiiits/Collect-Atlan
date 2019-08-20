from django.db import models

import datetime

# Create your models here.

class Task(models.Model):

    task_id = models.CharField(max_length=500, null=False, blank=False)
    task_type = models.CharField(max_length=100)
    file_url = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.task_id + "-" + self.task_type
    

class CSVData(models.Model):

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    data = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.task.task_id + "-" + self.task.task_type + ": " + self.data
