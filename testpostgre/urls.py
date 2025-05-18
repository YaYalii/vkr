"""
URL configuration for testpostgre project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from app.views import chat, GigaSearchView

import app.views

urlpatterns = [
    path('api/giga-search/', GigaSearchView.as_view(), name='giga-search'),
    path('download/<int:bell_id>/', views.download_recording, name='download_recording'),
    path('report/average-duration/', views.average_duration_report, name='average_duration_report'),
    path('admin/', admin.site.urls),
    path('report/', views.employees_list, name='report'),
    path('chat/', views.chat, name='chat'),
    path('', views.bells_list, name='main_page'),
]
