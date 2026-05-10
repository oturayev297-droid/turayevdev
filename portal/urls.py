from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('resume/', views.resume, name='resume'),
    path('projects/', views.projects, name='projects'),
    path('contact/', views.contact_view, name='contact'),
    path('ai-chat/', views.ai_chat_handler, name='ai_chat'),
]
