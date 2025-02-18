from django.db import models
from django.contrib.auth.models import User

class UserType(models.TextChoices):
    EMPLOYER = 'EMPLOYER', 'Employer'
    APPLICANT = 'APPLICANT', 'Applicant'

# Create your models here.
class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    company_logo = models.ImageField(upload_to="company_logo/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.company_name
    
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('INTERNSHIP', 'Internship'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', "Draft"),
        ('PUBLISHED', 'Published'),
        ('CLOSED', 'Closed')
    ]
    
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='FULL_TIME')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"
    
    class Meta:
        ordering = ['-created_at']
    
class Application(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('REVIEWED', 'Reviewed'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('ACCEPTED', 'Accepted'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    applied_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        full_name = self.applicant.get_full_name()
        if not full_name:
            full_name = self.applicant.username
        return f"{full_name} - {self.job.title}"
    
    class Meta:
        ordering = ["-applied_at"]
        unique_together = ['job', 'applicant'] # Prevent multiple applications for the same job

class Applicant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="applicant_resumes/", blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
