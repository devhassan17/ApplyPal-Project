

from django.db import models
from django.contrib.auth.models import User

# University Model
class University(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)  # Store hashed password
    calendly_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# User Model (Admin for University)
class UniversityAdmin(models.Model):
    university = models.ForeignKey(University, related_name="admins", on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admin: {self.user.username} for {self.university.name}"


# Iframe Generation Model
class Iframe(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    iframe_code = models.TextField()  # The generated iframe HTML code
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Iframe for {self.university.name}"


# Visitor Tracking Model
class Visitor(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=255)
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Visitor from {self.country} to {self.university.name}"


# Appointment Booking Model
class Appointment(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    visitor_ip = models.GenericIPAddressField()  # IP address of the student
    visitor_email = models.EmailField()  # Email of the student booking the appointment
    appointment_date = models.DateTimeField()  # Date and time of the booked appointment
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment booked by {self.visitor_email} for {self.university.name}"


# Analytics Model
class Analytics(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    total_visits = models.IntegerField(default=0)
    total_appointments = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.university.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    institution_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return f"Profile of {self.user.username}"