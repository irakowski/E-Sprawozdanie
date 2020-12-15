from django.urls import path, include
from . import views

app_name = 'esfviewer'
urlpatterns = [
    path('upload/', views.UploadView.as_view(), name='upload'),
    path('report/', views.ReportView.as_view(), name='report') 

]