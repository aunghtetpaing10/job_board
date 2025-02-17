from rest_framework import serializers
from .models import Employer, Job, Application

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = "__all__"

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"

class Application(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"