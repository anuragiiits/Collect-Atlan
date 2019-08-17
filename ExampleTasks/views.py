from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views import View
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .tasks import upload_csv
from .models import CSVData, Task

import csv
import json
import codecs

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
            CSVData.objects.filter(task_id=task_id).delete()
            return render(self.request, "cancel_task.html", context = {"task_id": task_id, "msg": "The Task is Cancelled"})
        else:
            return render(self.request, "cancel_task.html", context = {"task_id": task_id, "msg": "The Task has Already Finished/Stopped"})


class Example1View(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Example1View, self).dispatch(request, *args, **kwargs)

    def post(self, request):

        file_ptr = request.FILES['csv_data'] 

        if file_ptr is None:
            return HttpResponseRedirect(reverse('ExampleTasks:home', kwargs={'error': "Upload given CSV file only"}))
        
        # files = self.request.FILES['datafile']   
        with open(str(file_ptr),"r",) as fl:
            print("Fl = ", fl, codecs.iterdecode(file_ptr, 'utf-8'))
            # filereader = csv.reader(codecs.iterdecode(file_ptr, 'utf-8'))
            row_count = sum(1 for row in fl )
            print("Yes")
            task_id = upload_csv.delay("filereader", row_count)
            task = Task(str(task_id), "Upload CSV File")
            task.save()

            return render(request, "cancel_task.html", context = {"task_id": task_id, "msg":""})
        
        return HttpResponseRedirect(reverse('ExampleTasks:home', kwargs={'error': "Upload given CSV file only"}))
