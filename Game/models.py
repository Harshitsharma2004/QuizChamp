from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import datetime
from django.utils.timezone import now

class Interest(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    mobile_no = models.CharField(max_length=15, unique=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    hobbies = models.TextField(blank=True)
    qualification = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    interests = models.ManyToManyField(Interest, blank=True)
    email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
        self.otp_created_at = now()
        self.save(update_fields=["otp", "otp_created_at"])
    
    def is_otp_valid(self, entered_otp):
        if self.otp and self.otp_created_at:
            time_elapsed = (now() - self.otp_created_at).seconds
            return self.otp == entered_otp and time_elapsed <= 300  # Valid for 5 minutes
        return False

    def __str__(self):
        return self.username
    

# Questions 
class Category(models.Model):
    name = models.CharField(max_length=100)
    background_image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.name
    
class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question_text = models.TextField()
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):  
        return self.question_text

class QuizResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)