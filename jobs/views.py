from .serializers import EmployerSerializer, JobSerializer, ApplicationSerializer
from .models import Employer, Job, Application
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create your views here.
class EmployerListCreate(generics.ListCreateAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    
class EmployerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Employer.objects.filter(user=self.request.user)
    

class JobListCreate(generics.ListCreateAPIView):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        # Only show published jobs by default
        queryset = Job.objects.filter(status='PUBLISHED')
        
        job_type = self.request.query_params.get('job_type', None)
        if job_type:
            queryset = Job.objects.filter(job_type=job_type)

        location = self.request.query_params.get('location', None)
        if location:
            queryset = Job.objects.filter(location=location)
            
        return queryset
    
    def perform_create(self, serializer):
        try:
            employer = Employer.objects.get(user=self.request.user)
            serializer.save(employer=employer)
        except Employer.DoesNotExist:
            raise PermissionDenied("Only employer can create job listings")
        

class JobRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Employer can see all their jobs incliding drafts
            try:
                employer = Employer.objects.get(user=self.request.user)
                return Job.objects.filter(employer=employer)
            except Employer.DoesNotExist:
                return Job.objects.filter(status='PUBLISHED')
        return Job.objects.filter(status='PUBLISHED')
    

class ApplicationListCreate(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            # If the user is an employer
            employer = Employer.objects.get(user=user)
            return Application.objects.filter(job__employer=employer)
        except Employer.DoesNotExist:
            # If the user is an applicant
            return Application.objects.filter(applicant=user)
        
    def perform_create(self, serializer):
        user = self.request.user
        job = get_object_or_404(Job, pk=self.request.data.get('job'))
        
        # Check if the job is still accepting applications
        if job.status != 'PUBLISHED':
            raise PermissionDenied("This job is not accepting applications")
        if job.deadline and job.deadline < timezone.now().date():
            raise PermissionDenied("The application deadline has passed")
        
        # Check if the user already applied
        if Application.objects.filter(job=job, applicant=user).exists():
            raise PermissionDenied("You have already applied for this job")
        
        serializer.save(applicant=user, job=job)  
        

class ApplicationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employer = Employer.objects.get(user=user)
            return Application.objects.filter(job__employer=employer)
        except Employer.DoesNotExist:
            return Application.objects.filter(applicant=user)
        
    def perform_create(self, serializer):
        user = self.request.user
        try:
            employer = Employer.objects.get(user=user)
            if serializer.instance.job.employer == employer:
                serializer.save()
            else:
                raise PermissionDenied("You can only update applications for your own jobs")
        except Employer.DoesNotExist:
            raise PermissionDenied("Only employers can update application status")
