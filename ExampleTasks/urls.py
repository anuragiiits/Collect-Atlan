from django.urls import path

from .views import *

app_name = 'Atlan'

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('example1/', Example1And2View.as_view(), name="example1"),
    path('example2/', Example2View.as_view(), name="example2"),
    path('stop/<task_id>/', StopTaskView.as_view(), name="stop"),
    path('poll_for_download/<task_id>/', Example2Util.as_view(), name="example2util")
]
