from django.urls import path, include
from . import views

app_name = 'esfviewer'
urlpatterns = [
    path('upload/', views.FormView.as_view(), name='upload'), 

]