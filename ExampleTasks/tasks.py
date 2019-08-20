from django.conf import settings

from faker import Faker
from tqdm import tqdm
from celery import shared_task

from .models import CSVData, Task

import os
import csv
import datetime

@shared_task
def upload_csv(uploaded_file_url):

    if(uploaded_file_url[0] == '/' or uploaded_file_url[0] == '\\'):
        file_url = uploaded_file_url[1:]
    file_path = os.path.join(settings.BASE_DIR, str(file_url))
    
    fake = Faker()
    start_date = datetime.date(year=2000, month=1, day=1)
    end_date = datetime.date(year=2020, month=12, day=31)

    with open(file_path,"r",) as fl:
        file_reader = csv.reader(fl)
        row_count = sum(1 for row in fl)
        fl.seek(0)
        print(row_count)
        csv_data = []
        count = 0
        task_id = str(upload_csv.request.id)
        task, created = Task.objects.get_or_create(task_id = task_id, defaults = {"task_type": "Upload CSV File", "file_url": uploaded_file_url})
        print(created, file_reader, fl)
        iterator = tqdm(file_reader,total=row_count)
        for row in iterator:
            csv_data.append(row[0])
            count += 1
            if(count%100 is 0):
                objs = [CSVData(task=task, data=item, date=fake.date_between(start_date=start_date, end_date=end_date)) for item in csv_data]
                CSVData.objects.bulk_create(objs)
                csv_data = []
                count = 0
    
        objs = [CSVData(task=task, data=item, date=fake.date_between(start_date=start_date, end_date=end_date)) for item in csv_data]    #To insert the remaining data
        if len(objs) > 0:  
            CSVData.objects.bulk_create(objs)


@shared_task
def generate_file(start_date, end_date):
    filename = "%s.csv" % generate_file.request.id

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    csv_data = CSVData.objects.filter(date__gte=start_date, date__lte=end_date)

    file_path = os.path.join(settings.MEDIA_ROOT, str(filename))

    with open(file_path, "w+") as fl:
        writer = csv.writer(fl, dialect=csv.excel)
        iterator = tqdm(csv_data, total=len(csv_data))
        for i in iterator:
            writer.writerow([i.id, i.task.task_id, i.data, i.date])

    return filename
