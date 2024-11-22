from django.utils.timezone import now
from django.db import models
import uuid
from django.contrib.auth.models import User

# University Model
class University(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # For university admin
    password_hash = models.CharField(max_length=255)  # Store hashed password
    calendly_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
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


# InteractionType Choices
class InteractionType(models.TextChoices):
    YES = 'yes', 'Yes'
    NO = 'no', 'No'


# Tracking Model
class Tracking(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name="tracking_records")
    interaction_type = models.CharField(
        max_length=10,
        choices=InteractionType.choices,
        default=InteractionType.NO,
    )
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=255, default="Unknown")
    time = models.DateTimeField(default=now)

    def __str__(self):
        return f"Tracking Record - University ID: {self.university.id}, Interaction: {self.interaction_type}"
