from celery import shared_task
from .models import CSVData
from tqdm import tqdm

@shared_task
def upload_csv(file_reader, row_count):
    iterator = tqdm(file_reader,total=row_count)
    data = []
    count = 0
    task_id = upload_csv.request.id
    for row in iterator:
        data.append(row[0])
        count += 1
        if(count%100 is 0):
            objs = [CSVData(task_id, item) for item in data]
            CSVData.objects.bulk_create(objs)
            data = []
            count = 0
    
    objs = [CSVData(task_id, item) for item in data]    #To insert the remaining data
    CSVData.objects.bulk_create(objs)

