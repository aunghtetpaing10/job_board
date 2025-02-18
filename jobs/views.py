from .serializers import EmployerSerializer, JobSerializer, ApplicationSerializer, UserSerializer, ApplicantSerializer
from .models import Employer, Job, Application, Applicant
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Create your views here.
class EmployerPublicView(generics.RetrieveAPIView):
    """View for retrieving public employer information"""
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [permissions.AllowAny]
    
class EmployerRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_object(self):
        try:
            return Employer.objects.get(user=self.request.user)
        except Employer.DoesNotExist:
            raise PermissionDenied("Only employers can access this endpoint")
    

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
    
    def perform_update(self, serializer):
        try:
            employer = Employer.objects.get(user=self.request.user)
            if serializer.instance.employer == employer:
                serializer.save()
            else:
                raise PermissionDenied("You can only update your own job listings")
        except Employer.DoesNotExist:
            raise PermissionDenied("Only employers can update job listings")
    

class UserApplicationList(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        try:
            employer = Employer.objects.get(user=user)
            return Application.objects.filter(job__employer=employer)
        except Employer.DoesNotExist:
            return Application.objects.filter(applicant=user)
    

class ApplicationListCreate(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        job_pk = self.kwargs.get('job_pk')
        user = self.request.user
        try:
            # If the user is an employer
            employer = Employer.objects.get(user=user)
            return Application.objects.filter(job__employer=employer, job_id=job_pk)
        except Employer.DoesNotExist:
            # If the user is an applicant
            return Application.objects.filter(applicant=user, job_id=job_pk)
        
    def perform_create(self, serializer):
        user = self.request.user
        job_pk = self.kwargs.get('job_pk')
        job = get_object_or_404(Job, pk=job_pk)
        
        # Check if user is an employer
        if Employer.objects.filter(user=user).exists():
            raise PermissionDenied("Employers cannot apply to job listings")
        
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
        job_pk = self.kwargs.get('job_pk')
        try:
            employer = Employer.objects.get(user=user)
            return Application.objects.filter(job__employer=employer, job_id=job_pk)
        except Employer.DoesNotExist:
            return Application.objects.filter(applicant=user, job_id=job_pk)
        
    def perform_update(self, serializer):
        user = self.request.user
        try:
            employer = Employer.objects.get(user=user)
            if serializer.instance.job.employer == employer:
                serializer.save()
            else:
                raise PermissionDenied("You can only update applications for your own jobs")
        except Employer.DoesNotExist:
            raise PermissionDenied("Only employers can update application status")

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return appropriate profile based on user type
        if hasattr(user, 'employer'):
            profile_serializer = EmployerSerializer(user.employer)
        else:
            profile_serializer = ApplicantSerializer(user.applicant)
            
        return Response({
            'user': UserSerializer(user).data,
            'profile': profile_serializer.data
        }, status=status.HTTP_201_CREATED)

class ApplicantProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ApplicantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return Applicant.objects.get(user=self.request.user)
        except Applicant.DoesNotExist:
            raise PermissionDenied("Only applicants can access this endpoint")

class ApplicantListView(generics.ListAPIView):
    serializer_class = ApplicantSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Applicant.objects.all()
    
    def get_queryset(self):
        # Only employers should be able to list all applicants
        if not Employer.objects.filter(user=self.request.user).exists():
            raise PermissionDenied("Only employers can view all applicants")
        return super().get_queryset()
