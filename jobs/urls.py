from django.urls import path
from . import views

urlpatterns = [
    path('employers/', views.EmployerListCreate.as_view(), name='employer-list'),
    path('employers/<int:pk>/', views.EmployerRetrieveUpdateDestroy.as_view(), name='employer-detail'),
    path('jobs/', views.JobListCreate.as_view(), name='job-list'),
    path('jobs/<int:pk>/', views.JobRetrieveUpdateDestroy.as_view(), name='job-detail'),
    path('applications/', views.UserApplicationList.as_view(), name='user-applications'),
    path('jobs/<int:job_pk>/applications/', views.ApplicationListCreate.as_view(), name='application-list'),
    path('jobs/<int:job_pk>/applications/<int:pk>/', views.ApplicationRetrieveUpdateDestroy.as_view(), name='application-detail'),
]