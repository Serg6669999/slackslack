from django.urls import path
from . import views


urlpatterns = [
    # path('', views.start, name='page'),
    path('slack_chatme', views.slack_chatme, name='slack_chatme'),
    ]
