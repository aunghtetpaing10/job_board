from rest_framework import serializers
from .models import Employer, Job, Application
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        field = ["id", "username", "first_name", "last_name", "email"]

class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Employer
        fields = "__all__"

class JobSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    employer_id = serializers.PrimaryKeyRelatedField(
        queryset=Employer.objects.all(),
        write_only=True,
        source="employer"
    )
    
    class Meta:
        model = Job
        fields = "__all__"

class ApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    job_id = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        write_only=True,
        source="job"
    )
    
    class Meta:
        model = Application
        fields = "__all__"