from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from tqdm import tqdm

from .tasks import upload_csv
from .models import CSVData, Task

import os
import csv
import json
import codecs
import time

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


class Example1View(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example1View, self).dispatch(request, *args, **kwargs)

    def post(self, request):

        csv_file = request.FILES['csv_data'] 

        if csv_file is None:
            return render(request, "home.html", context = {'error': "Upload given CSV file only"})
            # return HttpResponseRedirect(reverse('Atlan:home', kwargs={'error': "Upload given CSV file only"}))
        
        if not csv_file.name.endswith('.csv'):
            return render(request, "home.html", context = {'error': "Upload given CSV file only"})
            # return HttpResponseRedirect(reverse('Atlan:home', kwargs={'error': "Upload given CSV file only"}))
        
        fs = FileSystemStorage()
        filename = fs.save(csv_file.name, csv_file)
        uploaded_file_url = fs.url(filename)

        task_id = upload_csv.delay(uploaded_file_url)
        Task.objects.get_or_create(task_id = task_id, defaults = {"task_type": "Upload CSV File", "file_url": uploaded_file_url})

        return render(request, "cancel_task.html", context = {"task_id": task_id, "msg":""})
