from django.urls import path
from issues import views

urlpatterns = [
    path('reporters/', views.reporters),
    path('issues/', views.issues),
]
