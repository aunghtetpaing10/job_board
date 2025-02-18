from django.urls import path
from . import views

urlpatterns = [
    path('employers/<int:pk>/', views.EmployerPublicView.as_view(), name='employer-public'),
    path('employer/profile/', views.EmployerRetrieveUpdateDestroy.as_view(), name='employer-profile'),
    path('jobs/', views.JobListCreate.as_view(), name='job-list'),
    path('jobs/<int:pk>/', views.JobRetrieveUpdateDestroy.as_view(), name='job-detail'),
    path('applications/', views.UserApplicationList.as_view(), name='user-applications'),
    path('jobs/<int:job_pk>/applications/', views.ApplicationListCreate.as_view(), name='application-list'),
    path('jobs/<int:job_pk>/applications/<int:pk>/', views.ApplicationRetrieveUpdateDestroy.as_view(), name='application-detail'),
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('applicants/', views.ApplicantListView.as_view(), name='applicant-list'),
    path('applicant/profile/', views.ApplicantProfileView.as_view(), name='applicant-profile'),
]