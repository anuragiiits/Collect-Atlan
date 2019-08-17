from django.urls import path

from .views import *

app_name = 'Atlan'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('example1/', Example1View.as_view(), name="example1"),
    path('stop/<task_id>/', StopTaskView.as_view(), name="stop")
]