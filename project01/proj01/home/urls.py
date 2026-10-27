from django.urls import path,include
from . import views

app_name=''
urlpatterns = [
    path('', views.index, name='index'),
    path('main1/', views.main1, name='main1'),
]
