from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views import View
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from tqdm import tqdm
from celery.task.control import revoke
from celery.result import AsyncResult

from .tasks import upload_csv, generate_file
from .models import CSVData, Task

import os
import csv
import json
import datetime


class HomeView(TemplateView):
    '''
        Renders the Home Page
    '''
    template_name = "home.html"


class StopTaskView(View):
    '''
        The view responsible to stop the task
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StopTaskView, self).dispatch(request, *args, **kwargs)

    '''
        Receives GET request with task_id in URL
    '''
    def get(self, request, task_id):
        state = AsyncResult(task_id).state  #Fetch the current state of the task
        if(state == "PENDING" or state == "STARTED" or state == "RETRY"):   #If the task is not finished/stopped yet
            revoke(task_id, terminate=True)     #Stops the task process
            CSVData.objects.filter(task__task_id=task_id).delete()  #Deletes all the data added to database during execution of this task
            return render(self.request, "cancel_task.html", context = {"task_id": task_id, "msg": "The Task is Cancelled"})
        else:
            return render(self.request, "cancel_task.html", context = {"task_id": task_id, "msg": "The Task has Already Finished/Stopped"})


class Example1And3View(View):
    '''
        The view with implementation of Example 1 and 3 problem
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example1And3View, self).dispatch(request, *args, **kwargs)

    '''
        Accepts POST request with File in it
    '''
    def post(self, request):
        csv_file = request.FILES['csv_data'] 
        # Validations for CSV File
        if csv_file is None:
            return render(request, "home.html", context = {'error': "Upload given CSV file only"})
        
        if not csv_file.name.endswith('.csv'):
            return render(request, "home.html", context = {'error': "Upload given CSV file only"})
        
        # Stores the Uploded file temporarily in Project File System Storage
        fs = FileSystemStorage()
        filename = fs.save(csv_file.name, csv_file)
        uploaded_file_url = fs.url(filename)    #gives the URL of file's temporary location

        # Makes Asynchronous Call through Celery to process the Uploaded File
        task_id = upload_csv.delay(uploaded_file_url)  
        # Stores the Task metadata in database for reference
        Task.objects.get_or_create(task_id = task_id, defaults = {"task_type": "Upload CSV File", "file_url": uploaded_file_url})

        # Redirect to cancel task page so that user can cancel the task while its processing
        return render(request, "cancel_task.html", context = {"task_id": task_id, "msg":"You can check the progress bar of uploading in the Celery Worker's Terminal"})


class Example2View(View):
    '''
        The view with implementation of Example 2 problem
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example2View, self).dispatch(request, *args, **kwargs)

    '''
        Accepts POST request with Start Date and End Date as flters
    '''
    def post(self, request):
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        try:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')  # Validation for Start Date
            datetime.datetime.strptime(end_date, '%Y-%m-%d')    # Validation for End Date
        except ValueError:
            return render(request, "home.html", context = {'error_2': "Invalid Date or Wrong Format, Please follow: YYYY-MM-DD"})

        # Make Asynchronous call to generate the CSV downloadable file
        task_id = generate_file.delay(start_date, end_date)
        download_file_url = os.path.join(settings.MEDIA_ROOT, "{}.csv".format(task_id))
        # Stores the Task metadata in database for reference
        Task.objects.create(task_id = task_id, task_type = "Download CSV File", file_url= download_file_url)
        
        # Redirect to cancel task page so that user can cancel the task while its processing
        return render(request, "poll_for_download_and_cancel.html", context = {"task_id": task_id, "msg":""})

class Example2Util(View):
    '''
        A utility class for Example 2 Task
        It is responsible to download the file once the asynchronous task has finished processing in background
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example2Util, self).dispatch(request, *args, **kwargs)

    def get(self, request, task_id):
        filename = request.GET.get("filename")
        # Listens to the ajax call made from client to check if task has finished processing
        if request.is_ajax():
            result = generate_file.AsyncResult(task_id)
            if result.state == "SUCCESS":   #If task is finished
                # Sends the filename to client
                return HttpResponse(json.dumps({"filename": result.get()}))
            return HttpResponse(json.dumps({"filename": None}))

        # If the request is not ajax, i.e., the task is completed and the request is to download the file
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, str(filename))
            f = open(file_path)
        except:
            return HttpResponseForbidden()
        else:
            response = HttpResponse(f, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response    # responses with the csv file
