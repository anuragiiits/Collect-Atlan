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
    '''
        For Example 1 & 3
        Stores the csv data uploaded by user in database
        Same data is later used for Example 2
    '''
    if(uploaded_file_url[0] == '/' or uploaded_file_url[0] == '\\'): # To remove the prefix slash for proper path joining
        file_url = uploaded_file_url[1:]
    file_path = os.path.join(settings.BASE_DIR, str(file_url))
    
    fake = Faker()  # generates random date that is used to generate downloadable data for Example 2
    start_date = datetime.date(year=2000, month=1, day=1)
    end_date = datetime.date(year=2020, month=12, day=31)

    with open(file_path,"r",) as fl:
        file_reader = csv.reader(fl)
        row_count = sum(1 for row in fl)
        fl.seek(0)
        csv_data = []
        count = 0
        task_id = str(upload_csv.request.id)
        task, created = Task.objects.get_or_create(task_id = task_id, defaults = {"task_type": "Upload CSV File", "file_url": uploaded_file_url})
        # tqdm iterator to visually show the process status as progress bar
        iterator = tqdm(file_reader,total=row_count)    
        for row in iterator:
            csv_data.append(row[0]) # gather data to store in database (this date is later used for example 2)
            count += 1
            '''
            Stores 100 objects at a time instead of storing data one by one
            This is done to improve the efficiency as bulk insertion is much efficient that multiple single uploads
            '''
            if(count%100 is 0): 
                objs = [CSVData(task=task, data=item, date=fake.date_between(start_date=start_date, end_date=end_date)) for item in csv_data]
                CSVData.objects.bulk_create(objs)   # bulk insertion of data
                csv_data = []
                count = 0

        # Insert the remaining data
        objs = [CSVData(task=task, data=item, date=fake.date_between(start_date=start_date, end_date=end_date)) for item in csv_data]    #To insert the remaining data
        if len(objs) > 0:  
            CSVData.objects.bulk_create(objs)


@shared_task
def generate_file(start_date, end_date):
    '''
        Generates the downloadable data based on the given start date and end date filters
    '''
    filename = "%s.csv" % generate_file.request.id  # filename as task id

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    # Filter the data of which file is to be created
    csv_data = CSVData.objects.filter(date__gte=start_date, date__lte=end_date)

    file_path = os.path.join(settings.MEDIA_ROOT, str(filename))

    with open(file_path, "w+") as fl:   # Generates the file
        writer = csv.writer(fl, dialect=csv.excel)
        # tqdm iterator to show progress bar of process
        iterator = tqdm(csv_data, total=len(csv_data))
        for i in iterator:
            writer.writerow([i.id, i.task.task_id, i.data, i.date])

    return filename
