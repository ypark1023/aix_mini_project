from django.urls import path,include
from . import views

app_name = 'tour'
urlpatterns = [
    path('gw_list10/', views.gw_list10, name='gw_list10'),
]
