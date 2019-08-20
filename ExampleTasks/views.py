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

from .tasks import upload_csv, generate_file
from .models import CSVData, Task

import os
import csv
import json
import datetime

from celery.task.control import revoke
from celery.result import AsyncResult


class HomeView(TemplateView):
    template_name = "home.html"


class StopTaskView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StopTaskView, self).dispatch(request, *args, **kwargs)

    def get(self, request, task_id):
        state = AsyncResult(task_id).state
        print(state)
        if(state == "PENDING" or state == "STARTED" or state == "RETRY"):
            revoke(task_id, terminate=True)
            CSVData.objects.filter(task__task_id=task_id).delete()
            return render(self.request, "cancel_task.html", context = {"task_id": task_id, "msg": "The Task is Cancelled"})
        else:
            return render(self.request, "cancel_task.html", context = {"task_id": task_id, "msg": "The Task has Already Finished/Stopped"})


class Example1And2View(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example1And2View, self).dispatch(request, *args, **kwargs)

    def post(self, request):

        csv_file = request.FILES['csv_data'] 

        if csv_file is None:
            return render(request, "home.html", context = {'error': "Upload given CSV file only"})
        
        if not csv_file.name.endswith('.csv'):
            return render(request, "home.html", context = {'error': "Upload given CSV file only"})
        
        fs = FileSystemStorage()
        filename = fs.save(csv_file.name, csv_file)
        uploaded_file_url = fs.url(filename)

        task_id = upload_csv.delay(uploaded_file_url)
        Task.objects.get_or_create(task_id = task_id, defaults = {"task_type": "Upload CSV File", "file_url": uploaded_file_url})

        return render(request, "cancel_task.html", context = {"task_id": task_id, "msg":"You can check the progress bar of uploading in the Celery Worker's Terminal"})


class Example2View(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example2View, self).dispatch(request, *args, **kwargs)

    def post(self, request):

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        try:
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return render(request, "home.html", context = {'error_2': "Invalid Date or Wrong Format, Please follow: YYYY-MM-DD"})

        task_id = generate_file.delay(start_date, end_date)
        download_file_url = os.path.join(settings.MEDIA_ROOT, "{}.csv".format(task_id))
        Task.objects.create(task_id = task_id, task_type = "Download CSV File", file_url= download_file_url)
        return render(request, "poll_for_download_and_cancel.html", context = {"task_id": task_id, "msg":""})

class Example2Util(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example2Util, self).dispatch(request, *args, **kwargs)

    def get(self, request, task_id):

        filename = request.GET.get("filename")
        if request.is_ajax():
            result = generate_file.AsyncResult(task_id)
            if result.state == "SUCCESS":
                return HttpResponse(json.dumps({"filename": result.get()}))
            return HttpResponse(json.dumps({"filename": None}))

        try:
            file_path = os.path.join(settings.MEDIA_ROOT, str(filename))
            f = open(file_path)
        except:
            return HttpResponseForbidden()
        else:
            response = HttpResponse(f, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
