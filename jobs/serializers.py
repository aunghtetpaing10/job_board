from rest_framework import serializers
from .models import Employer, Job, Application, Applicant, UserType
from django.contrib.auth.models import User
from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=UserType.choices, write_only=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password", "user_type"]
        
    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        password = validated_data.pop('password')
        
        with transaction.atomic():
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            
            if user_type == UserType.EMPLOYER:
                Employer.objects.create(user=user)
            else:
                Applicant.objects.create(user=user)
                
        return user

class ApplicantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Applicant
        fields = "__all__"

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
        source="job",
        required=False
    )
    cover_letter = serializers.CharField(required=False)
    resume = serializers.FileField(required=False)
    status = serializers.CharField(required=False)
    
    class Meta:
        model = Application
        fields = "__all__"